import os
import asyncio
from aiohttp import web

PORT = int(os.environ.get("PORT", 3000))
TOKEN = os.environ.get("TOKEN", "ech123456")

async def http_handler(request):
    if request.path == "/":
        return web.Response(text="Hello-world")
    elif request.path == "/stats":
        return web.json_response({"status": "running"})
    return web.Response(status=404, text="Not Found")

async def ws_handler(request):
    ws = web.WebSocketResponse()
    # 验证 token
    if TOKEN and request.headers.get("Sec-WebSocket-Protocol") != TOKEN:
        await ws.close()
        return ws
    await ws.prepare(request)
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            await ws.send_str(msg.data)
        elif msg.type == web.WSMsgType.BINARY:
            await ws.send_bytes(msg.data)
        elif msg.type == web.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())
    return ws

app = web.Application()
app.router.add_get('/', http_handler)
app.router.add_get('/stats', http_handler)
app.router.add_get('/ech', ws_handler)

if __name__ == "__main__":
    web.run_app(app, host='0.0.0.0', port=PORT)
