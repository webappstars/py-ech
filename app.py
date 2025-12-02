import os
import asyncio
from aiohttp import web
import websockets

# 环境变量
PORT = int(os.environ.get("PORT", 3000))
TOKEN = os.environ.get("TOKEN", "ech123456")

# HTTP 处理
async def http_handler(request):
    if request.path == "/":
        return web.Response(text="Hello-world")
    elif request.path == "/stats":
        return web.json_response({"status": "running"})
    return web.Response(status=404, text="Not Found")

# WebSocket 处理
async def ws_handler(websocket, path):
    if TOKEN and websocket.request_headers.get("Sec-WebSocket-Protocol") != TOKEN:
        await websocket.close()
        return
    try:
        async for message in websocket:
            await websocket.send(message)
    except:
        pass

async def main():
    # aiohttp HTTP server
    app = web.Application()
    app.router.add_get('/', http_handler)
    app.router.add_get('/stats', http_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

    # WebSocket server
    ws_server = await websockets.serve(
        ws_handler, '0.0.0.0', PORT, subprotocols=[TOKEN]
    )

    print(f"Server running on port {PORT} (HTTP + WS /ech)")
    await asyncio.Future()  # Keep running

if __name__ == "__main__":
    asyncio.run(main())
