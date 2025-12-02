import os
import asyncio
import time
import json
from http import HTTPStatus
from urllib.parse import urlparse
import socket
import aiohttp
import websockets
from websockets import WebSocketServerProtocol

# Environment variables
PORT = int(os.environ.get("PORT", 3000))
TOKEN = os.environ.get("TOKEN", "ech123456")
CF_FALLBACK_IPS = os.environ.get("CF_FALLBACK_IPS", "").split(",") if os.environ.get("CF_FALLBACK_IPS") else ["ProxyIP.JP.CMLiussss.net"]
DOH_SERVERS = [
    "https://cloudflare-dns.com/dns-query",
    "https://dns.google/dns-query",
    "https://1.1.1.1/dns-query"
]

DNS_CACHE = {}
DNS_CACHE_TTL = 300000  # in milliseconds

# Simple HTTP Handler
async def http_handler(reader, writer):
    try:
        data = await reader.read(1024)
        if not data:
            writer.close()
            await writer.wait_closed()
            return

        request_line = data.decode().splitlines()[0]
        method, path, _ = request_line.split()
        
        # Check WebSocket upgrade
        if "Upgrade: websocket" in data.decode() and path == "/ech":
            # Handle WS in a separate coroutine
            ws_server = await websockets.server.server(ws_handler, PORT, process_request=None, create_protocol=None)
            await ws_server.wait_closed()
            return

        # HTTP response
        if path == "/":
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello-world"
        elif path == "/stats":
            stats = {
                "dns_cache_size": len(DNS_CACHE),
                "doh_servers": DOH_SERVERS
            }
            response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{json.dumps(stats)}"
        else:
            response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nNot Found"
        writer.write(response.encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    except Exception as e:
        print(f"HTTP Error: {e}")

# DoH resolver
async def resolve_doh(hostname):
    now = time.time()
    if hostname in DNS_CACHE:
        entry = DNS_CACHE[hostname]
        if now - entry["timestamp"] < DNS_CACHE_TTL / 1000:
            print(f"[DoH Cache Hit] {hostname} -> {entry['ip']}")
            return entry["ip"]

    print(f"[DoH Query] Resolving {hostname}")
    async with aiohttp.ClientSession() as session:
        for server in DOH_SERVERS:
            try:
                url = f"{server}?name={hostname}&type=A"
                async with session.get(url, headers={"Accept": "application/dns-json"}, timeout=5) as resp:
                    data = await resp.json()
                    for answer in data.get("Answer", []):
                        if answer["type"] == 1:
                            ip = answer["data"]
                            DNS_CACHE[hostname] = {"ip": ip, "timestamp": now}
                            print(f"[DoH Success] {hostname} -> {ip} (via {server})")
                            return ip
            except Exception as e:
                print(f"[DoH Failed] {server}: {e}")

    # fallback system DNS
    try:
        ip = socket.gethostbyname(hostname)
        DNS_CACHE[hostname] = {"ip": ip, "timestamp": now}
        print(f"[DoH Fallback] Using system DNS for {hostname} -> {ip}")
        return ip
    except Exception as e:
        print(f"[DNS Error] Failed to resolve {hostname}: {e}")
        raise

# WebSocket echo handler
async def ws_handler(ws: WebSocketServerProtocol, path):
    if TOKEN and ws.subprotocol != TOKEN:
        await ws.close()
        return
    try:
        async for message in ws:
            await ws.send(message)
    except Exception:
        pass

# Run single port server
async def main():
    print(f"HTTP + WebSocket server running on port {PORT}, token {'enabled' if TOKEN else 'disabled'}")
    print(f"DoH servers: {DOH_SERVERS}, DNS cache TTL: {DNS_CACHE_TTL/1000}s")
    server = await asyncio.start_server(http_handler, "0.0.0.0", PORT)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
