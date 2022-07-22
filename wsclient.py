import asyncio
import websockets
 
async def test():
	async with websockets.connect('ws://localhost:4000') as websocket:
		response = await websocket.recv()
		print(response)

while True:
	asyncio.get_event_loop().run_until_complete(test())
