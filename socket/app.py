import asyncio
import json
import os.path
import random
import secrets
import sqlite3
import subprocess

import websockets

from Card import Card, Rank, Color
from Game import Game
from Player import Player
from User import User
from GamePhaseDeck import GamePhaseDeck

connected = set()
socket_to_player_id = {}

DEFAULT_PHASE_LIST = [
	"S3+S3",
	"S3+R4",
	"S4+R4",
	"R7",
	"R8",
	"R9",
	"S4+S4",
	"C7",
	"S5+S2",
	"S5+S3",
]

INITIAL_HAND_SIZE = 10
# We'll start from a new database everytime we start the server
# This is just until we can get something that definitely works
if os.path.exists("phase_ten.db"):
	os.remove("phase_ten.db")

con = sqlite3.connect("phase_ten.db")
# con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute(
	"CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL, token TEXT NOT NULL);"
)
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_name ON users (name);")
cur.execute(
	"CREATE TABLE IF NOT EXISTS games ("
	"	id TEXT NOT NULL,"
	"	phase_list TEXT NOT NULL,"
	"	deck TEXT NOT NULL,"
	"	discard TEXT NOT NULL,"
	"	current_player TEXT NOT NULL,"
	"	owner TEXT NOT NULL,"
	"	in_progress INTEGER DEFAULT (0) NOT NULL,"
	"	CONSTRAINT games_pk PRIMARY KEY (id),"
	"	CONSTRAINT games_users_FK FOREIGN KEY (owner) REFERENCES users(id)"
	");"
)
cur.execute(
	"CREATE TABLE IF NOT EXISTS gameHits ("
	"	id TEXT NOT NULL,"
	"	game TEXT NOT NULL,"
	"	phase TEXT NOT NULL,"
	"	deck TEXT NOT NULL,"
	"	CONSTRAINT gameHits_pk PRIMARY KEY (id),"
	"	CONSTRAINT gameHits_games_FK FOREIGN KEY (game) REFERENCES games(id)"
	");"
)
cur.execute(
	"CREATE TABLE IF NOT EXISTS players ("
	"	id TEXT NOT NULL,"
	"	game_id TEXT NOT NULL,"
	"	user_id TEXT NOT NULL,"
	"	hand TEXT NOT NULL,"
	"	turn_index INTEGER DEFAULT (-1) NOT NULL,"
	"	phase_index INTEGER DEFAULT (0) NOT NULL,"
	"	drew_card INTEGER DEFAULT (0) NOT NULL,"
	"	completed_phase INTEGER DEFAULT (0) NOT NULL,"
	"	skip_cards INTEGER DEFAULT (0) NOT NULL,"
	"	CONSTRAINT players_pk PRIMARY KEY (id),"
	"	CONSTRAINT players_games_FK FOREIGN KEY (game_id) REFERENCES games(id),"
	"	CONSTRAINT players_users_FK FOREIGN KEY (user_id) REFERENCES users(id)"
	");"
)
cur.execute(
	"CREATE UNIQUE INDEX IF NOT EXISTS players_game_id_IDX ON players (game_id,user_id);"
)
cur.execute(
	"""CREATE TABLE IF NOT EXISTS gamePhaseDecks (
	"id"	TEXT NOT NULL,
	"game_id"	TEXT,
	"phase"	TEXT NOT NULL,
	"deck"	TEXT NOT NULL,
	CONSTRAINT gamesPhaseDecks_games_FK FOREIGN KEY(game_id) REFERENCES games(id),
	CONSTRAINT gamePhaseDecks PRIMARY KEY("id")
);""")
con.commit()


def id_to_user(user_id: str) -> User:
	for (id, name, token) in list(cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))):
		u = User(id, name, token)
		return u


def name_in_user(name: str) -> bool:
	return not (cur.execute("SELECT * FROM users WHERE name = ?",
	                        (name,)).fetchone() is None)


def name_to_user(name: str) -> User:
	for (id, name, token) in list(cur.execute("SELECT * FROM users WHERE name = ?", (name,))):
		u = User(id, name, token)
		return u


async def send_users():
	user_list = [User(id, name, token) for (id, name, token) in cur.execute("SELECT * FROM users")]
	websockets.broadcast(connected, json.dumps({"type": "get_users", "users": [u.toJSONDict() for u in user_list]}))

async def send_players():
	for (socket, player_id) in socket_to_player_id.items():


		player = id_to_player(player_id)
		game = id_to_game(player.game_id)
		user_id = player.user_id
		game_id = game.id
		player_dict = player.toJSONDict()
		if player.phase_index < len(game.phase_list):
			player_dict["phase"] = game.phase_list[player.phase_index]
		else:
			player_dict["phase"] = "WINNER"

		await socket.send(json.dumps(
			{
				"type": "get_player",
				"game_id": game_id,
				"user_id": user_id,
				"player": player_dict,
			}
		))

def id_to_game(game_id: str) -> Game:
	for (id, phase_list, deck_json, discard_json, current_player, owner, in_progress) in list(cur.execute(
			"SELECT * FROM games WHERE id = ?", (game_id,))):
		deck = [Card.fromJSONDict(x) for x in json.loads(deck_json)]
		discard = [Card.fromJSONDict(x) for x in json.loads(discard_json)]
		game = Game(id, json.loads(phase_list), deck, discard, current_player, owner, in_progress)
		return game

	raise Exception(f"{game_id} is not a valid game id!")


def get_games():
	game_set = []
	for (id, phase_list, deck_json, discard_json, current_player, owner, in_progress) in cur.execute(
			"SELECT * FROM games"):
		deck = [Card.fromJSONDict(x) for x in json.loads(deck_json)]
		discard = [Card.fromJSONDict(x) for x in json.loads(discard_json)]
		game = Game(id, json.loads(phase_list), deck, discard, current_player, owner, in_progress)
		game_set.append(game)
	return game_set


def id_to_gamePhaseDeck(gamePhaseDeck_id: str) -> GamePhaseDeck:
	for (id, game_id, phase, deck_json) in list(
			cur.execute("SELECT id, game_id, phase, deck FROM gamePhaseDecks WHERE id = ?", (gamePhaseDeck_id,))):
		deck = [Card.fromJSONDict(x) for x in json.loads(deck_json)]
		phaseDeck = GamePhaseDeck(id, game_id, phase, deck)
		return phaseDeck


def game_id_to_gamePhaseDecks(game_id: str):
	phaseDeck_set = []
	for (id, phase, deck_json) in list(
			cur.execute("SELECT id, phase, deck FROM gamePhaseDecks WHERE game_id = ?", (game_id,))):
		deck = [Card.fromJSONDict(x) for x in json.loads(deck_json)]
		phaseDeck = GamePhaseDeck(id, game_id, phase, deck)
		phaseDeck_set.append(phaseDeck)
	return phaseDeck_set


def game_id_to_players(game_id):
	player_list = []

	for (id, user_id, json_hand, turn_index, phase_index, drew_card, completed_phase, skip_cards) in list(
			cur.execute(
				"SELECT players.id, user_id, hand, turn_index, phase_index, drew_card, completed_phase, skip_cards "
				"FROM players JOIN users ON players.user_id = users.id WHERE game_id = ? ORDER BY turn_index;",
				(game_id,))):
		hand = [Card.fromJSONDict(x) for x in json.loads(json_hand)]
		player = Player(id, game_id, user_id, hand, turn_index, phase_index, drew_card == 1, completed_phase == 1,
		                skip_cards)
		player_list.append(player)

	return player_list


async def send_games():
	game_list = []
	for game in get_games():
		game_dict = game.toJSONDict()
		game_dict["users"] = []
		user_id_list = list(cur.execute(
			"SELECT users.id FROM users JOIN players ON users.id = players.user_id JOIN games ON players.game_id = games.id WHERE games.id = ?",
			(game.id,)
		))
		for (user_id,) in user_id_list:
			game_dict["users"].append(id_to_user(user_id).toJSONDict())

		game_dict["players"] = []
		for (player_id, user_id, user_name, turn_index, phase_index, skip_cards) in list(
				cur.execute("SELECT players.id, users.id, users.name, turn_index, phase_index, skip_cards "
				            "FROM players JOIN users WHERE players.user_id = users.id AND "
				            "players.game_id = ? ORDER BY turn_index;", (game.id,))):
			game_dict["players"].append(
				{"player_id": player_id, "user_id": user_id, "name": user_name, "turn_index": turn_index,
				 "phase_index": phase_index,
				 "skip_cards": skip_cards})

		game_dict["phase_decks"] = [x.toJSONDict() for x in game_id_to_gamePhaseDecks(game.id)]
		game_list.append(game_dict)

	websockets.broadcast(
		connected, json.dumps({"type": "get_games", "games": game_list})
	)


def id_to_player(player_id: str) -> Player:
	for (id, game_id, user_id, hand_json, turn_index, phase_index, drew_deck, completed_phase, skip_cards) in list(
			cur.execute(
				"SELECT * FROM players WHERE id = ?", (player_id,))):
		hand = [Card.fromJSONDict(x) for x in json.loads(hand_json)]
		p = Player(id, game_id, user_id, hand, turn_index, phase_index, drew_deck, completed_phase, skip_cards)
		return p


def game_user_id_to_player(game_id: str, user_id: str) -> Player:
	for (id, game_id, user_id, hand_json, turn_index, phase_index, drew_deck, completed_phase, skip_cards) in list(
			cur.execute(
				"SELECT * FROM players WHERE game_id = ? AND user_id = ?", (game_id, user_id))):
		hand = [Card.fromJSONDict(x) for x in json.loads(hand_json)]
		p = Player(id, game_id, user_id, hand, turn_index, phase_index, drew_deck, completed_phase, skip_cards)
		return p


def game_user_id_in_player(game_id: str, user_id: str) -> bool:
	return not (cur.execute("SELECT * FROM players WHERE game_id = ? AND user_id = ?",
	                        (game_id, user_id)).fetchone() is None)


def create_game(data):
	user_id = data["user_id"]
	if cur.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone() is None:
		return json.dumps(
			{
				"type": "rejection",
				"message": f"User ID {user_id} is not valid!",
			}
		)
	else:
		g = Game(secrets.token_urlsafe(16), DEFAULT_PHASE_LIST, [], [], 0, user_id, False)
		try:
			cur.execute(
				"INSERT INTO games (id, phase_list, deck, discard, current_player, owner, in_progress) VALUES (?, ?, ?, ?, ?, ?, ?)",
				(g.id, json.dumps(DEFAULT_PHASE_LIST), "[]", "[]", user_id, user_id, 0))

			p = Player(secrets.token_urlsafe(16), g.id, user_id)
			cur.execute(
				"INSERT INTO players (id, game_id, user_id, hand) VALUES (?, ?, ?, ?)", (p.id, g.id, user_id, "[]")
			)
			con.commit()
			# For each game, let's also list the players who are in it
			game_dict = g.toJSONDict()
			game_dict["users"] = []
			for (user_id,) in cur.execute(
					f"SELECT users.id FROM users JOIN players ON users.id = players.user_id JOIN games ON players.game_id = games.id WHERE games.id = ?;",
					(g.id,)
			):
				game_dict["users"].append(id_to_user(user_id).toJSONDict())

			return json.dumps({"type": "create_game", "game": game_dict})

		except Exception as e:
			raise e
			return json.dumps({"type": "rejection", "message": "Cannot create game"})


def player_action(data):
	player_id = data["player_id"]
	(game_id, user_id) = cur.execute("SELECT game_id, user_id FROM players WHERE id = ?", (player_id,)).fetchone()
	player = id_to_player(player_id)
	hand = player.hand
	game = id_to_game(game_id)

	complete_turn = False

	# Players are always allowed to sort their cards
	# Any other action requires you to wait until your turn
	if data["action"] == "sort_by_color":
		hand.sort(key=lambda x: x.color.value)
		json_hand = [x.toJSONDict() for x in hand]
		cur.execute("UPDATE players SET hand=? WHERE id = ?",
		            (json.dumps(json_hand), player_id))
		con.commit()
	elif data["action"] == "sort_by_rank":
		hand.sort(key=lambda x: x.rank.value)
		json_hand = [x.toJSONDict() for x in hand]
		cur.execute("UPDATE players SET hand=? WHERE id = ?",
		            (json.dumps(json_hand), player_id))
		con.commit()
	elif game.current_player != player.user_id:
		return json.dumps({"type": "rejection", "message": "It's not your turn"})

	# The only action possible is do_skip when you are skipped
	if data["action"] != "do_skip" and player.skip_cards > 0:
		data["action"] = "do_skip"

	match data["action"]:
		case "draw_deck":
			# You can only draw once per turn
			if player.drew_card:
				return json.dumps({"type": "rejection", "message": "You already drew for this round!"})
			hand.append(game.deck.pop())
			json_hand = [x.toJSONDict() for x in hand]
			player.drew_card = True
			cur.execute("UPDATE players SET hand=?, drew_card=1 WHERE id = ?",
			            (json.dumps(json_hand), player_id))
			json_deck = [x.toJSONDict() for x in game.deck]
			cur.execute("UPDATE games SET deck=? WHERE id = ?",
			            (json.dumps(json_deck), game_id))
			con.commit()

		case "draw_discard":
			# You can only draw once per turn
			if player.drew_card:
				return json.dumps({"type": "rejection", "message": "You already drew for this round!"})
			if len(game.discard) == 0:
				return json.dumps({"type": "rejection", "message": "Can't take from an empty discard pile!"})
			if game.discard[-1].rank is Rank.SKIP:
				return json.dumps({"type": "rejection", "message": "Can't take SKIP cards from the discard pile!"})
			hand.append(game.discard.pop())
			json_hand = [x.toJSONDict() for x in hand]
			player.drew_card = True
			cur.execute("UPDATE players SET hand=?, drew_card=1 WHERE id = ?",
			            (json.dumps(json_hand), player_id))
			json_discard = [x.toJSONDict() for x in game.discard]
			cur.execute("UPDATE games SET discard=? WHERE id = ?",
			            (json.dumps(json_discard), game_id))
			con.commit()
		case "do_skip":
			pass

		case "put_down":
			if not player.completed_phase:
				return json.dumps(
					{"type": "rejection", "message": "You need to complete your phase before you put down"})

			gamePhaseDeck = id_to_gamePhaseDeck(data["phase_deck_id"])
			cards = [Card.fromJSONDict(x) for x in data["cards"]]
			str_cards = [str(x) for x in cards]
			str_gamePhaseDeck = [str(x) for x in gamePhaseDeck.deck]

			deckToTest = None
			str_deckToTest = []
			if data["direction"] == "start":
				deckToTest = cards + gamePhaseDeck.deck
				str_deckToTest = str_cards + str_gamePhaseDeck
			elif data["direction"] == "end":
				deckToTest = gamePhaseDeck.deck + cards
				str_deckToTest = str_gamePhaseDeck + str_cards
			else:
				return json.dumps({"type": "rejection", "message": f"{data['direction']} is not a valid direction"})

			phase = gamePhaseDeck.phase

			command = f"java RE -p {phase} -d {' '.join(str_deckToTest)}"
			output = subprocess.check_output(command, shell=True).decode("utf-8").strip()
			if output == "true":
				# Remove the cards from the player's hand
				for card in cards:
					if card not in hand:
						return json.dumps({"type": "rejection", "message": f"{str(card)} is not in your hand"})
					else:
						hand.remove(card)
				json_hand = [x.toJSONDict() for x in hand]
				cur.execute("UPDATE players SET hand=? WHERE id = ?",
				            (json.dumps(json_hand), player_id))

				json_deckToTest = [x.toJSONDict() for x in deckToTest]
				cur.execute("UPDATE gamePhaseDecks SET deck=? WHERE id = ?",
				            (json.dumps(json_deckToTest), data["phase_deck_id"]))
				con.commit()


			else:
				return json.dumps({"type": "rejection", "message": "Unable to put down these cards to the phase!"})

		case "complete_phase":
			if player.completed_phase:
				return json.dumps({"type": "rejection", "message": "You've already completed your phase!"})

			cards = [Card.fromJSONDict(x) for x in data["cards"]]
			str_cards = [str(x) for x in cards]
			phase = game.phase_list[player.phase_index]
			command = f"java RE -p {phase} -d {' '.join(str_cards)}"
			output = subprocess.check_output(command, shell=True).decode("utf-8").strip()
			if output == "true":

				for phase_comp in phase.split('+'):

					num_cards = int(phase_comp[1:])

					card_component = cards[:num_cards]
					# Remove the cards from the player's hand
					for card in card_component:
						if card not in hand:
							return json.dumps(
								{"type": "rejection", "message": f"This card {card} is not in your hand!"})
						hand.remove(card)
					player.completed_phase = True
					cards = cards[num_cards:]
					# Create a new gamePhaseDeck
					json_cards = [x.toJSONDict() for x in card_component]
					cur.execute("INSERT INTO gamePhaseDecks (id, game_id, phase, deck) VALUES (?, ?, ?, ?)",
					            (secrets.token_urlsafe(16), game_id, phase_comp[:1], json.dumps(json_cards)))

					json_hand = [x.toJSONDict() for x in hand]
					cur.execute("UPDATE players SET hand=?, completed_phase=1 WHERE id = ?",
					            (json.dumps(json_hand), player_id))
					con.commit()



			else:
				return json.dumps({"type": "rejection", "message": "Not a valid phase!"})

		case "skip_player":
			if not player.drew_card:
				return json.dumps({"type": "rejection", "message": "Draw a card before you attempt to skip someone"})
			contains_skip = False
			skip_card = None
			for card in hand:
				if card.rank is Rank.SKIP:
					contains_skip = True
					skip_card = card
					break
			if contains_skip:
				# Give the other player a skip card
				to_id = data["to"]
				to_player = game_user_id_to_player(game_id, to_id)
				to_player.skip_cards += 1
				hand.remove(skip_card)
				json_hand = [x.toJSONDict() for x in hand]

				cur.execute("UPDATE players SET skip_cards=? WHERE id = ?",
				            (to_player.skip_cards, to_player.id))
				cur.execute("UPDATE players SET hand=? WHERE id = ?",
				            (json.dumps(json_hand), player_id))
				con.commit()
				complete_turn = True

			else:
				return json.dumps({"type": "rejection", "message": "You don't have a skip card!"})

		case "discard":
			card_id = data["card_id"]
			selected_card = None
			for card in hand:
				if card.id == card_id:
					selected_card = card
					break
			if selected_card is not None:
				hand.remove(selected_card)
				game.discard.append(selected_card)

				json_hand = [x.toJSONDict() for x in hand]
				cur.execute("UPDATE players SET hand=? WHERE id = ?",
				            (json.dumps(json_hand), player_id))

				json_discard = [x.toJSONDict() for x in game.discard]
				cur.execute("UPDATE games SET discard=? WHERE id = ?",
				            (json.dumps(json_discard), game_id))
				con.commit()
			complete_turn = True

		case "finish_hand":
			pass
		case "sort_by_color":
			pass
		case "sort_by_rank":
			pass
		case _:
			raise Exception(f"Unrecognized player option {data['action']}")

	# User had discarded, skipped, or been skipped
	# We need to advance the game to the next player
	if complete_turn:
		roomPlayers = game_id_to_players(game.id)
		current_player_index = -1
		for i, roomPlayer in enumerate(roomPlayers):
			if roomPlayer.user_id == game.current_player:
				current_player_index = i
				break
		if i == -1:
			raise Exception(f"Couldn't find the current player!")

		current_player_index = (current_player_index + 1) % len(roomPlayers)
		next_player = roomPlayers[current_player_index]

		# Perform the skipping operations
		while next_player.skip_cards > 0:
			next_player.skip_cards -= 1
			next_player.drew_card = False
			game.discard.append(Card(Color.SKIP, Rank.SKIP))
			cur.execute("UPDATE players SET skip_cards=?, drew_card=0 WHERE id=?",
			            (next_player.skip_cards, next_player.id))
			con.commit()
			current_player_index = (current_player_index + 1) % len(roomPlayers)
			next_player = roomPlayers[current_player_index]

		game.current_player = next_player.user_id
		player.drew_card = False

		cur.execute("UPDATE games SET current_player=? WHERE id = ?", (game.current_player, game.id))
		cur.execute("UPDATE players SET drew_card=0 WHERE id=?", (player.id,))
		json_discard = [x.toJSONDict() for x in game.discard]
		cur.execute("UPDATE games SET discard=? WHERE id = ?",
		            (json.dumps(json_discard), game_id))
		con.commit()

	# Player has completed their hand
	if len(player.hand) == 0:
		game.deck = Card.getNewDeck()
		random.shuffle(game.deck)
		game.discard = [game.deck.pop()]

		# Other players lost, so we'll set their index to 0
		cur.execute("UPDATE players SET phase_index=0 WHERE game_id=? AND id != ?",
		            (game_id, player_id))

		roomPlayers = game_id_to_players(game.id)
		# Update the player info
		for i, roomPlayer in enumerate(roomPlayers):
			roomPlayer.hand = [game.deck.pop() for _ in range(INITIAL_HAND_SIZE)]
			roomPlayer.drew_card = False
			# We move the player list up one turn
			roomPlayer.turn_index = (i + 1) % len(roomPlayers)
			if roomPlayer.completed_phase:
				roomPlayer.phase_index += 1
				roomPlayer.completed_phase = False
				roomPlayer.skip_cards = 0

			json_hand = [x.toJSONDict() for x in roomPlayer.hand]
			cur.execute("UPDATE players SET hand=?,turn_index=?,phase_index=?,drew_card=0,completed_phase=0,"
			            "skip_cards=0 WHERE id=?",
			            (json.dumps(json_hand), roomPlayer.turn_index, roomPlayer.phase_index, roomPlayer.id))

		game.current_player = roomPlayers[-1].user_id
		# Remove all phase decks
		cur.execute("DELETE FROM gamePhaseDecks WHERE game_id=?", (game.id,))
		json_deck = [x.toJSONDict() for x in game.deck]
		json_discard = [x.toJSONDict() for x in game.discard]
		cur.execute("UPDATE games SET deck=?,discard=?,current_player=? WHERE id=?",
		            (json.dumps(json_deck), json.dumps([ ]), game.current_player, game.id))
		con.commit()

	player_dict = player.toJSONDict()
	player_dict["phase"] = game.phase_list[player.phase_index]
	return json.dumps({"type": "get_player", "game_id": game_id, "user_id": user_id, "player": player_dict})


def handle_data(data, websocket):
	print()
	print(data)

	match data["type"]:
		case "connection":
			return json.dumps({"type": "connection"})
		case "disconnection":
			connected.remove(websocket)
		case "new_user":
			will_send = True
			if will_send:
				u = User(
					secrets.token_urlsafe(16),
					data["name"],
					secrets.token_urlsafe(16),
				)
				try:
					# Add this new user to our databases
					cur.execute(
						"INSERT INTO users (id, name, token) VALUES (?, ?, ?);",
						(u.id, u.name, u.token),
					)
					con.commit()
					return json.dumps({"type": "new_user", "user": u.toJSONDict()})


				except Exception as e:
					# This happens because the SQL statement failed
					print(e)
					return json.dumps(
						{
							"type": "rejection",
							"message": f"User already exists with the name {data['name']}",
						}
					)
			else:
				return json.dumps(
					{
						"type": "rejection",
						"message": f"User already exists with the name {data['name']}",
					}
				)

		case "get_users":
			return json.dumps({"type": "ignore"})
		case "get_player":
			game_id = data["game_id"]
			user_id = data["user_id"]
			game = id_to_game(game_id)
			if game_user_id_in_player(game_id, user_id):
				player = game_user_id_to_player(game_id, user_id)
				socket_to_player_id[websocket] = player.id
				player_dict = player.toJSONDict()
				if player.phase_index < len(game.phase_list):
					player_dict["phase"] = game.phase_list[player.phase_index]
				else:
					player_dict["phase"] = "WINNER"

				return json.dumps(
					{
						"type": "get_player",
						"game_id": game_id,
						"user_id": user_id,
						"player": player_dict,
					}
				)
			else:
				return json.dumps(
					{
						"type": "get_player",
						"game_id": game_id,
						"user_id": user_id,
					}
				)

		case "create_game":
			return create_game(data)

		case "join_game":
			game_id = data["game_id"]
			user_id = data["user_id"]
			game = id_to_game(game_id)

			if game_user_id_in_player(game_id, user_id):
				return json.dumps(
					{
						"type": "rejection",
						"message": "You are already in that game!",
					}
				)
			elif game.in_progress:
				return json.dumps(
					{
						"type": "rejection",
						"message": "You can't join a game that's already in progress",
					}
				)
			else:
				try:
					p = Player(secrets.token_urlsafe(16), game_id, user_id)
					cur.execute("INSERT INTO players (id, game_id, user_id, hand) VALUES (?, ?, ?, ?)",
					            (p.id, game_id, user_id, "[]"))
					con.commit()

					return json.dumps({"type": "ignore"})
				except Exception as e:
					print(e)
					user = id_to_user(user_id)
					return json.dumps({"type": "rejection", "message": f"({user.name} cannot join game {game_id}"})
		case "unjoin_game":
			game_id = data["game_id"]
			user_id = data["user_id"]
			game = id_to_game(game_id)

			# The host is deleting the game
			if game.owner == user_id:
				dead_player_key_list = [
					player_id
					for player_id in cur.execute(
						f"SELECT game_id, user_id from players"
					)
				]
				cur.execute(f"DELETE FROM games WHERE id = '{game_id}'")
				cur.execute(f"DELETE FROM players WHERE game_id = '{game_id}'")
				con.commit()


			else:
				cur.execute(
					f"DELETE FROM players WHERE game_id = '{game_id}' AND user_id = '{user_id}'"
				)
				con.commit()

			return json.dumps({"type": "ignore"})
		case "get_games":
			return json.dumps({"type": "ignore"})

		case "start_game":
			game_id = data["game_id"]
			user_id = data["user_id"]

			game = id_to_game(game_id)

			if game.owner == user_id and not game.in_progress:
				game_user_id_list = list(
					cur.execute(f"SELECT game_id, user_id FROM players WHERE game_id = ?", (game_id,)))
				player_list = [
					game_user_id_to_player(game_id, user_id)
					for (game_id, user_id) in game_user_id_list
				]

				deck = Card.getNewDeck()
				random.shuffle(deck)
				random.shuffle(player_list)
				for i, player in enumerate(player_list):
					player.phase_index = 0
					player.turn_index = i
					player.hand = [deck.pop() for _ in range(INITIAL_HAND_SIZE)]
					json_hand = [x.toJSONDict() for x in player.hand]
					command = f"UPDATE players SET phase_index=0, turn_index={i}, hand='{json.dumps(json_hand)}' WHERE id = '{player.id}'"
					cur.execute(command)
					con.commit()

				game.discard = [deck.pop()]
				game.deck = deck
				game.in_progress = True
				game.current_player = player_list[0].user_id
				json_deck = [x.toJSONDict() for x in deck]
				json_discard = [x.toJSONDict() for x in game.discard]
				command = f"UPDATE games SET deck='{json.dumps(json_deck)}', discard='{json.dumps(json_discard)}', current_player='{player_list[0].user_id}', in_progress=1 WHERE id='{game.id}'"
				cur.execute(command)
				con.commit()
				return json.dumps({"type": "ignore"})
			else:
				return json.dumps(
					{
						"type": "rejection",
						"message": "You are not the owner and cannot start this game",
					}
				)
		case "player_action":
			return player_action(data)
		case _:
			return json.dumps(
				{
					"type": "rejection",
					"message": f"Unrecognized type {data['type']}",
				}
			)


async def handler(websocket):
	connected.add(websocket)

	# if True:
	try:
		while True:
			event = await websocket.recv()
			data = json.loads(event)
			message = handle_data(data, websocket)
			await websocket.send(message)
			await send_games()
			await send_users()
			await send_players()
	except Exception as e:
		print(e)
		if websocket in connected:
			connected.remove(websocket)
		if websocket in socket_to_player_id:
			socket_to_player_id.pop(websocket)
		raise e


async def main():
	async with websockets.serve(handler, "", 8001):
		await asyncio.Future()  # run forever


if __name__ == "__main__":
	# Create our Regular Expression Compiler for phases
	if not os.path.exists("RE.class"):
		subprocess.check_output(["javac", "RE.java"])

	if not name_in_user("Alfredo"):
		handle_data({"type": "new_user", "name": "Alfredo"}, None)
	if not name_in_user("Naly"):
		handle_data({"type": "new_user", "name": "Naly"}, None)
	if not name_in_user("Yer"):
		handle_data({"type": "new_user", "name": "Yer"}, None)
	if not name_in_user("Averie"):
		handle_data({"type": "new_user", "name": "Averie"}, None)

	alfredo = name_to_user("Alfredo")
	naly = name_to_user("Naly")
	yer = name_to_user("Yer")
	averie = name_to_user("Averie")

	handle_data({"type": "create_game", "user_id": alfredo.id}, None)
	game0 = get_games()[0]
	handle_data({"type": "create_game", "user_id": yer.id}, None)
	game1 = get_games()[0] if get_games()[0].id != game0.id else get_games()[1]

	handle_data({"type": "join_game", "user_id": naly.id, "game_id": game0.id}, None)
	handle_data({"type": "start_game", "user_id": alfredo.id, "game_id": game0.id}, None)
	handle_data({"type": "join_game", "user_id": alfredo.id, "game_id": game1.id}, None)
	handle_data({"type": "join_game", "user_id": naly.id, "game_id": game1.id}, None)
	handle_data({"type": "join_game", "user_id": averie.id, "game_id": game1.id}, None)
	handle_data({"type": "start_game", "user_id": yer.id, "game_id": game1.id}, None)
	game0 = id_to_game(game0.id)
	game1 = id_to_game(game1.id)

	alfredo_p = game_user_id_to_player(game0.id, alfredo.id)
	naly_p = game_user_id_to_player(game0.id, naly.id)

	asyncio.run(main())
