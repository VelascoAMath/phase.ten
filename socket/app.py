

import asyncio
import websockets
import json


async def handler(websocket):
    while True:
        message = await websocket.recv()
        message = json.loads(message)
        print(f"Received {message}")
        if message == "Hello!":
            continue
        await websocket.send(json.dumps(message))
        print(f"Sending {message}")



async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future() # run forever



if __name__ == "__main__":
    asyncio.run(main())



