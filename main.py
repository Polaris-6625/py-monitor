import asyncio
import websockets

async def echo(websocket, path):
    async for message in websocket:
        # 接收客户端的消息，然后原样返回
        await websocket.send(message)

start_server = websockets.serve(echo, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()