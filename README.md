# ECH + Cloudflared Dual-Service Docker Image

This project provides a Docker image that can run in a **non-root environment**, featuring:

- **ECH WebSocket server**
- **HTTP "Hello World" page**
- **Cloudflared tunnel proxy for ECH WebSocket**
- Automatic binary download (skips download if already present)
- Log management
- Weekly maintenance: clean logs and restart every Monday at 03:00 (Asia/Shanghai)

---

## Features

1. HTTP page: `http://<IP>:PORT` → displays `Hello World!`  
2. WebSocket: `ws://<IP>:WSPORT/ech` → connects to ECH Server  
3. Cloudflared tunnel only proxies the WebSocket port  
4. Supports environment variable configuration for TOKEN and Argo tunnel  
5. Automatic download of `ech-server` and `cloudflared` without manual installation  
6. Weekly log cleanup and service restart (Monday 03:00, UTC+8)  
7. Works in Docker / Railway / Fly.io / other non-root containers

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PORT | 3000 | HTTP page port |
| WSPORT | PORT+1 | WebSocket ECH port |
| TOKEN | "" | ECH authentication token |
| ARGO_AUTH | "" | Cloudflared Argo authentication (Token / JSON) |
| ARGO_DOMAIN | "" | Cloudflared domain |
| CUSTOM_DNS | "" | Custom DNS for ECH and Cloudflared |
| ECH_LOG | ech.log | ECH log file |
| ARGO_LOG | argo.log | Cloudflared log file |

---

## Usage Example

### Build Docker Image

```bash
docker build -t ech-tunnel .
```

### Run Container

```bash
docker run -d   -p 3000:3000   -p 3001:3001   -e PORT=3000   -e WSPORT=3001   -e CUSTOM_DNS=1.1.1.1   -e TOKEN="your-token"   -e ARGO_AUTH="your-argo-auth"   -e ARGO_DOMAIN="your.domain.com"   ech-tunnel
```

### Access Services

- HTTP page: `http://<IP>:3000`  
- WebSocket: `ws://<IP>:3001/ech`  

---

## Notes

- Ensure HTTP and WebSocket ports **do not conflict**  
- TOKEN and ARGO_AUTH **are not printed** to logs for security  
- Binary files are downloaded to `/app`, no root permission required  

---

## Project Structure

```
app.py
requirements.txt
Dockerfile
README.md
```
