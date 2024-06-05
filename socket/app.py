import asyncio
import json
import os.path
import secrets
import sqlite3

import websockets
from vel_data_structures import AVL_Set, AVL_Dict

from Game import Game
from Player import Player
from User import User

connected = set()

user_set = AVL_Set()
id_to_user = AVL_Dict()

player_set = AVL_Set()
id_to_player = AVL_Dict()

game_set = AVL_Set()
id_to_game = AVL_Dict()

DEFAULT_PHASE_LIST = ["S3+S3", "S3+R4", "S4+R4", "R7", "R8", "R9", "S4+S4", "C7", "S5+S2", "S5+S3"]

# We'll start from a new database everytime we start the server
# This is just until we can get something that definitely works
if os.path.exists("phase_ten.db"):
	os.remove("phase_ten.db")



async def send_games(cur, websocket):
	game_list = []
	for game in game_set:
		game_dict = game.toJSONDict()
		game_dict["users"] = []
		for (user_id,) in cur.execute(
			f"SELECT users.id FROM users JOIN players ON users.id = players.user_id JOIN games ON players.game_id = games.id WHERE games.id = '{game.id}';"):
			game_dict["users"].append(id_to_user[user_id].toJSONDict())
		game_list.append(game_dict)
	
	await websocket.send(json.dumps({"type": "get_games", "games": game_list}))

async def handler(websocket):
	connected.add(websocket)
	con = sqlite3.connect("phase_ten.db")
	# con = sqlite3.connect(":memory:")
	cur = con.cursor()
	cur.execute("CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, name TEXT)")
	cur.execute("CREATE TABLE IF NOT EXISTS games(id TEXT PRIMARY KEY)")
	cur.execute("CREATE TABLE IF NOT EXISTS players(id TEXT PRIMARY KEY, game_id TEXT, user_id TEXT,"
	            "FOREIGN KEY (game_id) REFERENCES games (id) ON DELETE CASCADE,"
	            "FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)")
	con.commit()
	
	# try:
	while True:
		event = await websocket.recv()
		data = json.loads(event)
		print()
		print(connected)
		print(f"user_set={user_set}")
		print(f"id_to_user={id_to_user}")
		print(f"player_set={player_set}")
		print(f"id_to_player={id_to_player}")
		print(f"game_set={game_set}")
		print(f"id_to_game={id_to_game}")
		print(data)
		
		if data["type"] == "new_user":
			will_send = True
			for u in user_set:
				if u.name == data["name"]:
					will_send = False
					break
			if will_send:
				u = User(secrets.token_urlsafe(16), data["name"], secrets.token_urlsafe(16))
				# Add this new user to our databases
				user_set.add(u)
				id_to_user[u.id] = u
				cur.execute(f"INSERT INTO users (id, name) VALUES ('{u.id}', '{u.name}')")
				con.commit()
				await websocket.send(json.dumps({"type": "new_user", "user": u.toJSONDict()}))
			else:
				await websocket.send(json.dumps(
					{"type": "rejection", "message": f"User already exists with the name {data['name']}"}))
		elif data["type"] == "get_users":
			await websocket.send(json.dumps({"type": "get_users", "users": [u.toJSONDict() for u in user_set]}))
		elif data["type"] == "create_game":
			user_id = data["user_id"]
			if user_id not in id_to_user:
				await websocket.send(json.dumps({"type": "rejection", "message": f"User ID {user_id} is not valid!"}))
			else:
				g = Game(secrets.token_urlsafe(16), DEFAULT_PHASE_LIST, [], [], 0)
				id_to_game[g.id] = g
				game_set.add(g)
				cur.execute(f"INSERT INTO games (id) VALUES ('{g.id}')")
				
				p = Player(secrets.token_urlsafe(16), user_id, g.id, [], 1, 0)
				player_set.add(p)
				id_to_player[(g.id, user_id)] = p
				cur.execute(f"INSERT INTO players (id, game_id, user_id) VALUES ('{p.id}', '{g.id}', '{user_id}')")
				con.commit()
				# For each game, let's also list the players who are in it
				game_dict = g.toJSONDict()
				game_dict["users"] = []
				for (user_id,) in cur.execute(
					f"SELECT users.id FROM users JOIN players ON users.id = players.user_id JOIN games ON players.game_id = games.id WHERE games.id = '{g.id}' ;"):
					game_dict["users"].append(id_to_user[user_id].toJSONDict())
				
				await websocket.send(json.dumps({"type": "create_game", "game": game_dict}))
		
		elif data["type"] == "join_game":
			game_id = data["game_id"]
			user_id = data["user_id"]
			
			if (game_id, user_id) in id_to_player:
				await websocket.send(json.dumps({"type": "rejection", "message": "You are already in that game!"}))
			else:
				p = Player(secrets.token_urlsafe(16), user_id, game_id, [], 1, 0)
				player_set.add(p)
				id_to_player[(game_id, user_id)] = p
				cur.execute(f"INSERT INTO players (id, game_id, user_id) VALUES ('{p.id}', '{game_id}', '{user_id}')")
				con.commit()
				
				await send_games(cur, websocket)
		
		elif data["type"] == "get_games":
			await send_games(cur, websocket)


# except Exception as e:
# 	print(e)
# 	if websocket in connected:
# 		connected.remove(websocket)


async def main():
	async with websockets.serve(handler, "", 8001):
		await asyncio.Future()  # run forever


if __name__ == "__main__":
	asyncio.run(main())
