import asyncio
import secrets

import websockets
import json

from vel_data_structures import AVL_Set

from Player import Player
from User import User

connected = set()

user_set = AVL_Set()
game_set = set()

async def handler(websocket):
	connected.add(websocket)
	
	try:
		while True:
			print(connected)
			print(user_set)
			event = await websocket.recv()
			data = json.loads(event)
			print(data)
			print(type(data))
			
			if data["type"] == "new_user":
				print(data)
				will_send = True
				for u in user_set:
					if u.name == data["name"]:
						will_send = False
						break
				if will_send:
					u = User(secrets.randbelow(2 ** 64 - 1), data["name"], secrets.token_urlsafe(16), [])
					user_set.add(u)
					await websocket.send(json.dumps({"type": "new_user", "user": u.toJSONDict()}))
				else:
					await websocket.send(json.dumps({"type": "rejection", "message": f"User already exists with the name {data['name']}"}))
			elif data["type"] == "get_users":
				await websocket.send(json.dumps({"type": "get_users", "users": [u.toJSONDict() for u in user_set]}))
	
	
	except Exception as e:
		print(e)
		if websocket in connected:
			connected.remove(websocket)


async def main():
	async with websockets.serve(handler, "", 8001):
		await asyncio.Future()  # run forever


if __name__ == "__main__":
	asyncio.run(main())
