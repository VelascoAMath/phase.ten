

import asyncio
import websockets
import json

connected = set()
socket_index = 0

async def handler(websocket):
    global socket_index
    index = socket_index
    socket_index += 1
    connected.add(websocket)
    try:
        while True:
            message = await websocket.recv()
            message = json.loads(message)
            print(f"Received {message}")
            if message == "Hello!":
                continue
            message = message + f" {index}"
            websockets.broadcast(connected, json.dumps(message))
            # await websocket.send(json.dumps(message))
            print(f"Sending {message}")
    finally:
     connected.remove(websocket)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future() # run forever



if __name__ == "__main__":
    asyncio.run(main())



