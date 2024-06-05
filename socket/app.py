import asyncio
import json
import secrets

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


async def handler(websocket):
	connected.add(websocket)

	# try:
	while True:
		event = await websocket.recv()
		data = json.loads(event)
		print()
		print(connected)
		print(f"{user_set=}")
		print(f"{id_to_user=}")
		print(f"{player_set}")
		print(f"{id_to_player=}")
		print(f"game_set={game_set}")
		print(f"{id_to_game=}")
		print(data)

		if data["type"] == "new_user":
			will_send = True
			for u in user_set:
				if u.name == data["name"]:
					will_send = False
					break
			if will_send:
				u = User(secrets.token_urlsafe(16), data["name"], secrets.token_urlsafe(16))
				user_set.add(u)
				id_to_user[u.id] = u
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

				p = Player(secrets.token_urlsafe(16), user_id, g.id, [], 1, 0)
				player_set.add(p)
				id_to_player[p.id] = p
				await websocket.send(json.dumps({"type": "create_game", "game": g.toJSONDict()}))

		elif data["type"] == "join_game":
			game_id = data["game_id"]
			player_id = data["user_id"]
		elif data["type"] == "get_games":
			await websocket.send(json.dumps({"type": "get_games", "games": [g.toJSONDict() for g in game_set]}))


# except Exception as e:
# 	print(e)
# 	if websocket in connected:
# 		connected.remove(websocket)


async def main():
	async with websockets.serve(handler, "", 8001):
		await asyncio.Future()  # run forever


if __name__ == "__main__":
	asyncio.run(main())
