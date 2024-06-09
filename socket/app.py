import asyncio
import json
import os.path
import random
import secrets
import sqlite3
import subprocess

import websockets
from vel_data_structures import AVL_Set, AVL_Dict

from Card import Card
from Game import Game
from Player import Player
from User import User

connected = set()

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


def id_to_user(user_id):
	for (id, name, token) in list(cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))):
		u = User(id, name, token)
		return u


def name_in_user(name):
	return not (cur.execute("SELECT * FROM users WHERE name = ?",
	                        (name,)).fetchone() is None)


def name_to_user(name):
	for (id, name, token) in list(cur.execute("SELECT * FROM users WHERE name = ?", (name,))):
		u = User(id, name, token)
		return u


async def send_users():
	user_list = [User(id, name, token) for (id, name, token) in cur.execute("SELECT * FROM users")]
	websockets.broadcast(connected, json.dumps({"type": "get_users", "users": [u.toJSONDict() for u in user_list]}))


def id_to_game(game_id):
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
		game_list.append(game_dict)

	websockets.broadcast(
		connected, json.dumps({"type": "get_games", "games": game_list})
	)


def id_to_player(player_id):
	for (id, game_id, user_id, hand_json, turn_index, phase_index, completed_phase, skip_cards) in list(cur.execute(
			"SELECT * FROM players WHERE id = ?", (player_id,))):
		hand = [Card.fromJSONDict(x) for x in json.loads(hand_json)]
		p = Player(id, game_id, user_id, hand, turn_index, phase_index, completed_phase, skip_cards)
		return p


def game_user_id_to_player(game_id, user_id):
	for (id, game_id, user_id, hand_json, turn_index, phase_index, completed_phase, skip_cards) in list(cur.execute(
			"SELECT * FROM players WHERE game_id = ? AND user_id = ?", (game_id, user_id))):
		hand = [Card.fromJSONDict(x) for x in json.loads(hand_json)]
		p = Player(id, game_id, user_id, hand, turn_index, phase_index, completed_phase, skip_cards)
		return p


def game_user_id_in_player(game_id, user_id):
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

	match data["action"]:
		case "sort_by_color":
			hand.sort(key=lambda x: x.color.value)
			json_hand = [x.toJSONDict() for x in hand]
			cur.execute("UPDATE players SET hand=? WHERE id = ?",
			            (json.dumps(json_hand), player_id))
		case "sort_by_rank":
			hand.sort(key=lambda x: x.rank.value)
			json_hand = [x.toJSONDict() for x in hand]
			cur.execute("UPDATE players SET hand=? WHERE id = ?",
			            (json.dumps(json_hand), player_id))
		case "draw_deck":
			hand.append(game.deck.pop())
			json_hand = [x.toJSONDict() for x in hand]
			cur.execute("UPDATE players SET hand=? WHERE id = ?",
			            (json.dumps(json_hand), player_id))
			json_deck = [x.toJSONDict() for x in game.deck]
			cur.execute("UPDATE games SET deck=? WHERE id = ?",
			            (json.dumps(json_deck), game_id))

		case "draw_discard":
			hand.append(game.discard.pop())
			json_hand = [x.toJSONDict() for x in hand]
			cur.execute("UPDATE players SET hand=? WHERE id = ?",
			            (json.dumps(json_hand), player_id))
			json_discard = [x.toJSONDict() for x in game.discard]
			cur.execute("UPDATE games SET discard=? WHERE id = ?",
			            (json.dumps(json_discard), game_id))
		case "do_skip":
			pass
		case "put_down":
			pass
		case "complete_phase":
			pass
		case "skip_player":
			pass
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


		case "finish_hand":
			pass
		case _:
			raise Exception(f"Unrecognized player option {data['action']}")
	return json.dumps({"type": "get_player", "game_id": game_id, "user_id": user_id, "player": player.toJSONDict()})


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
			if game_user_id_in_player(game_id, user_id):
				player = game_user_id_to_player(game_id, user_id)
				return json.dumps(
					{
						"type": "get_player",
						"game_id": game_id,
						"user_id": user_id,
						"player": player.toJSONDict(),
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
					player.hand = [deck.pop() for _ in range(10)]
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
	except Exception as e:
		print(e)
		if websocket in connected:
			connected.remove(websocket)
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

	alfredo = name_to_user("Alfredo")
	naly = name_to_user("Naly")

	handle_data({"type": "create_game", "user_id": alfredo.id}, None)
	game = get_games()[0]

	handle_data({"type": "join_game", "user_id": naly.id, "game_id": game.id}, None)
	handle_data({"type": "start_game", "user_id": alfredo.id, "game_id": game.id}, None)
	game = id_to_game(game.id)

	alfredo_p = game_user_id_to_player(game.id, alfredo.id)
	naly_p = game_user_id_to_player(game.id, naly.id)

	asyncio.run(main())
