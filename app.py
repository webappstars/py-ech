import os
from aiohttp import web

PORT = int(os.environ.get("PORT", 3000))
TOKEN = os.environ.get("TOKEN", "ech123456")

# HTTP Handler
async def http_handler(request):
    if request.path == "/":
        return web.Response(text="Hello-world")
    elif request.path == "/stats":
        return web.json_response({"status": "running"})
    return web.Response(status=404, text="Not Found")

# WebSocket Handler
async def ws_handler(request):
    ws = web.WebSocketResponse()
    # 验证 Token
    if TOKEN:
        client_token = request.headers.get("Sec-WebSocket-Protocol")
        if client_token != TOKEN:
            await ws.prepare(request)
            await ws.close(message=b"Invalid token")
            return ws

    await ws.prepare(request)
    
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                await ws.send_str(msg.data)  # Echo text
            elif msg.type == web.WSMsgType.BINARY:
                await ws.send_bytes(msg.data)  # Echo binary
            elif msg.type == web.WSMsgType.ERROR:
                print(f'WebSocket connection closed with exception {ws.exception()}')
    except Exception as e:
        print(f"WebSocket handler error: {e}")
    finally:
        await ws.close()
    return ws

# App setup
app = web.Application()
app.router.add_get('/', http_handler)
app.router.add_get('/stats', http_handler)
app.router.add_get('/ech', ws_handler)

if __name__ == "__main__":
    print(f"Server running on 0.0.0.0:{PORT} (HTTP + WS /ech)")
    web.run_app(app, host='0.0.0.0', port=PORT)
