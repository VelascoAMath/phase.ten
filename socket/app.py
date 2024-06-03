

import asyncio
import websockets
import json

connected = set()

async def handler(websocket):
    connected.add(websocket)

    try:
        while True:
            event = await websocket.recv()
            event = json.loads(event)
            
            print(event)
            
    finally:
        connected.remove(websocket)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future() # run forever



if __name__ == "__main__":
    asyncio.run(main())



