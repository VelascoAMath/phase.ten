import asyncio
import json
import os.path
import random
import secrets
import sqlite3
import subprocess
import uuid

import websockets

from Card import Card, Rank, Color
from Game import Game
from Player import Player
from User import User
from GamePhaseDeck import GamePhaseDeck

DEBUG = True

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
if DEBUG and os.path.exists("phase_ten.db"):
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
	"	winner TEXT,"
	"	CONSTRAINT games_pk PRIMARY KEY (id),"
	"	CONSTRAINT games_users_FK FOREIGN KEY (owner) REFERENCES users(id)"
	"	CONSTRAINT games_current_player_FK FOREIGN KEY (owner) REFERENCES users(id)"
	"	CONSTRAINT games_winner_FK FOREIGN KEY (owner) REFERENCES users(id)"
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
	CONSTRAINT gamePhaseDecks_pk PRIMARY KEY("id")
);""")
con.commit()

User.setCursor(cur)
Game.setCursor(cur)
Player.setCursor(cur)


async def send_users():
	user_list = User.all()
	websockets.broadcast(connected, json.dumps({"type": "get_users", "users": [u.toJSONDict() for u in user_list]}))


async def send_players():
	socket_to_delete = set()
	for (socket, player_id) in socket_to_player_id.items():
		
		player = Player.get_by_id(player_id)
		# This player is deleted
		# We'll need to send a different player to this socket
		if player is None:
			socket_to_delete.add(player)
			break
		game = Game.get_by_id(player.game_id)
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
				"game_id": str(game_id),
				"user_id": str(user_id),
				"player": player_dict,
			}
		))
		game_dict = Game.get_by_id(game_id).toJSONDict()
		
		# Don't send the entire deck
		if "deck" in game_dict:
			del game_dict["deck"]
		
		game_dict["players"] = []
		game_dict["users"] = []
		player_list = game.get_players()
		for player in player_list:
			user_dict = User.get_by_id(player.user_id).toJSONDict()
			player_dict = player.toJSONDict()
			player_dict["name"] = User.get_by_id(player.user_id).name
			
			if "hand" in player_dict:
				del player_dict["hand"]
			
			if "token" in user_dict:
				del user_dict["token"]
			
			game_dict["players"].append(player_dict)
			game_dict["users"].append(user_dict)
		
		game_dict["phase_decks"] = [x.toJSONDict() for x in game_id_to_gamePhaseDecks(str(game.id))]

		await socket.send(json.dumps(
			{
				"type": "get_game",
				"game": game_dict
			}
		))
		


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



async def send_games():
	game_list = []
	for game in Game.all():
		game_dict = game.toJSONDict()
		if "deck" in game_dict:
			del game_dict["deck"]
		if "discard" in game_dict:
			del game_dict["discard"]
		
		game_dict["users"] = []
		user_id_list = list(cur.execute(
			"SELECT users.id FROM users JOIN players ON users.id = players.user_id JOIN games ON players.game_id = games.id WHERE games.id = ?",
			(str(game.id),)
		))
		for (user_id,) in user_id_list:
			user_dict = User.get_by_id(user_id).toJSONDict()
			if "token" in user_dict:
				del user_dict["token"]
			game_dict["users"].append(user_dict)
		
		game_list.append(game_dict)
	
	websockets.broadcast(
		connected, json.dumps({"type": "get_games", "games": game_list})
	)


def create_game(data):
	user_id = data["user_id"]
	if not User.exists(user_id):
		return json.dumps(
			{
				"type": "rejection",
				"message": f"User ID {user_id} is not valid!",
			}
		)
	else:
		try:
			g = Game(phase_list=DEFAULT_PHASE_LIST, deck=[], discard=[], owner=user_id, current_player=user_id,
			         in_progress=False)
			g.save()
			
			p = Player(game_id=g.id, user_id=user_id)
			p.save()
			con.commit()
			# For each game, let's also list the players who are in it
			game_dict = g.toJSONDict()
			game_dict["users"] = []
			for (user_id,) in cur.execute(
				f"SELECT users.id FROM users JOIN players "
				"ON users.id = players.user_id JOIN games ON players.game_id = games.id WHERE games.id = ?;",
				(str(g.id),)
			):
				game_dict["users"].append(User.get_by_id(user_id).toJSONDict())
			
			return json.dumps({"type": "create_game", "game": game_dict})
		
		except Exception as e:
			raise e
			return json.dumps({"type": "rejection", "message": "Cannot create game"})


def player_action(data):
	player_id = data["player_id"]
	(game_id, user_id) = cur.execute("SELECT game_id, user_id FROM players WHERE id = ?", (player_id,)).fetchone()
	player = Player.get_by_id(player_id)
	hand = player.hand
	game = Game.get_by_id(game_id)
	
	complete_turn = False
	
	# Players are always allowed to sort their cards
	# Any other action requires you to wait until your turn
	is_sorting = False
	if data["action"] == "sort_by_color":
		hand.sort(key=lambda x: x.color.value)
		player.save()
		con.commit()
		is_sorting = True
	elif data["action"] == "sort_by_rank":
		hand.sort(key=lambda x: x.rank.value)
		player.save()
		con.commit()
		is_sorting = True
	elif game.current_player != player.user_id:
		return json.dumps({"type": "rejection", "message": "It's not your turn"})
	
	# The only action possible is do_skip when you are skipped
	if data["action"] != "do_skip" and player.skip_cards > 0:
		data["action"] = "do_skip"

	if not is_sorting:
		if (not (data["action"] == "draw_deck" or data["action"] == "draw_discard")) and not player.drew_card:
			return json.dumps({"type": "rejection", "message": "YOU HAVE TO DRAW FIRST!!!!"})
	
	match data["action"]:
		case "draw_deck":
			# You can only draw once per turn
			if player.drew_card:
				return json.dumps({"type": "rejection", "message": "You already drew for this round!"})
			hand.append(game.deck.pop())
			json_hand = [x.toJSONDict() for x in hand]
			player.drew_card = True
			player.save()
			game.save()
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
			player.save()
			game.save()
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
				player.save()
				
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
					player.save()
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
				to_player = Player.get_by_game_user_id(game_id, to_id)
				to_player.skip_cards += 1
				hand.remove(skip_card)
				
				player.save()
				to_player.save()
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
				player.save()
				game.save()
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
		roomPlayers = game.get_players()
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
			player.save()
			next_player.save()
			con.commit()
			current_player_index = (current_player_index + 1) % len(roomPlayers)
			next_player = roomPlayers[current_player_index]
		
		game.current_player = next_player.user_id
		player.drew_card = False
		
		player.save()
		game.save()
		con.commit()
	
	# Player has completed their hand
	if len(player.hand) == 0:
		game.deck = Card.getNewDeck()
		random.shuffle(game.deck)
		game.discard = [game.deck.pop()]
		
		# Player has won
		if player.phase_index >= len(game.phase_list) - 1 and player.completed_phase:
			game.winner = player.user_id
		else:
			roomPlayers = game.get_players()
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
				
				roomPlayer.save()
		
		game.current_player = roomPlayers[-1].user_id
		# Remove all phase decks
		cur.execute("DELETE FROM gamePhaseDecks WHERE game_id=?", (game.id,))
		game.save()
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
				try:
					# Add this new user to our databases
					u = User(
						id=uuid.uuid4(),
						name=data["name"],
					)
					u.save()
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
			
			if not Game.exists(game_id):
				return json.dumps({"type": "ignore", "message": f"Game room {game_id} is not valid!"})
			
			game = Game.get_by_id(game_id)
			if Player.exists_game_user(game_id, user_id):
				player = Player.get_by_game_user_id(game_id, user_id)
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
			game = Game.get_by_id(game_id)
			
			if Player.get_by_game_user_id(game_id, user_id):
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
					p = Player(game_id=game_id, user_id=user_id)
					p.save()
					con.commit()
					
					return json.dumps({"type": "ignore"})
				except Exception as e:
					print(e)
					user = User.get_by_id(user_id)
					return json.dumps({"type": "rejection", "message": f"({user.name} cannot join game {game_id}"})
		case "unjoin_game":
			game_id = data["game_id"]
			user_id = data["user_id"]
			game = Game.get_by_id(game_id)
			
			# The host is deleting the game
			if str(game.owner) == user_id:
				game.delete()
				con.commit()
			
			else:
				Player.get_by_game_user_id(game_id, user_id).delete()
				con.commit()
			
			return json.dumps({"type": "ignore"})
		case "get_games":
			return json.dumps({"type": "ignore"})
		
		case "start_game":
			game_id = data["game_id"]
			user_id = data["user_id"]
			
			game = Game.get_by_id(game_id)
			
			if str(game.owner) == user_id and not game.in_progress:
				game_user_id_list = list(
					cur.execute(f"SELECT game_id, user_id FROM players WHERE game_id = ?", (game_id,)))
				player_list = [
					Player.get_by_game_user_id(game_id, user_id)
					for (game_id, user_id) in game_user_id_list
				]
				
				deck = Card.getNewDeck()
				random.shuffle(deck)
				random.shuffle(player_list)
				for i, player in enumerate(player_list):
					player.phase_index = 0
					player.turn_index = i
					player.hand = [deck.pop() for _ in range(INITIAL_HAND_SIZE)]
					player.save()
					con.commit()
				
				game.discard = [deck.pop()]
				game.deck = deck
				game.in_progress = True
				game.current_player = player_list[0].user_id
				game.save()
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
			print(message)
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
	
	if DEBUG:
		# Create our users
		if not User.name_in_user("Alfredo"):
			handle_data({"type": "new_user", "name": "Alfredo"}, None)
		if not User.name_in_user("Naly"):
			handle_data({"type": "new_user", "name": "Naly"}, None)
		if not User.name_in_user("Yer"):
			handle_data({"type": "new_user", "name": "Yer"}, None)
		if not User.name_in_user("Averie"):
			handle_data({"type": "new_user", "name": "Averie"}, None)
		
		alfredo = User.name_to_user("Alfredo")
		naly = User.name_to_user("Naly")
		yer = User.name_to_user("Yer")
		averie = User.name_to_user("Averie")
		
		# Create a game
		handle_data({"type": "create_game", "user_id": str(alfredo.id)}, None)
		game0 = Game.all()[0]
		
		# Have a player join and unjoin
		handle_data({"type": "join_game", "user_id": str(naly.id), "game_id": str(game0.id)}, None)
		handle_data({"type": "unjoin_game", "user_id": str(naly.id), "game_id": str(game0.id)}, None)
		
		# Have a host delete an empty game room
		handle_data({"type": "unjoin_game", "user_id": str(alfredo.id), "game_id": str(game0.id)}, None)
		
		# Have a host delete a game that's started
		handle_data({"type": "create_game", "user_id": str(alfredo.id)}, None)
		game0 = Game.all()[0]
		handle_data({"type": "join_game", "user_id": str(naly.id), "game_id": str(game0.id)}, None)
		handle_data({"type": "start_game", "user_id": str(alfredo.id), "game_id": str(game0.id)}, None)
		handle_data({"type": "unjoin_game", "user_id": str(alfredo.id), "game_id": str(game0.id)}, None)
		
		# Create the game rooms for web-browser testing
		handle_data({"type": "create_game", "user_id": str(alfredo.id)}, None)
		game0 = Game.all()[0]
		handle_data({"type": "join_game", "user_id": str(naly.id), "game_id": str(game0.id)}, None)
		handle_data({"type": "create_game", "user_id": str(yer.id)}, None)
		game1 = Game.all()[0] if Game.all()[0].id != game0.id else Game.all()[1]
		
		handle_data({"type": "start_game", "user_id": str(alfredo.id), "game_id": str(game0.id)}, None)
		handle_data({"type": "join_game", "user_id": str(alfredo.id), "game_id": str(game1.id)}, None)
		handle_data({"type": "join_game", "user_id": str(naly.id), "game_id": str(game1.id)}, None)
		handle_data({"type": "join_game", "user_id": str(averie.id), "game_id": str(game1.id)}, None)
		handle_data({"type": "start_game", "user_id": str(yer.id), "game_id": str(game1.id)}, None)
		game0 = Game.get_by_id(game0.id)
		game1 = Game.get_by_id(game1.id)
		
		alfredo_p = Player.get_by_game_user_id(game0.id, alfredo.id)
		naly_p = Player.get_by_game_user_id(game0.id, naly.id)
	
	asyncio.run(main())
