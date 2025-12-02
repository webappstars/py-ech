#!/usr/bin/env python3
import os
import subprocess
import platform
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import pytz
import schedule

# ---------------- Environment ---------------- #
PORT = int(os.getenv("PORT", 3000))
WSPORT = int(os.getenv("WSPORT", PORT + 1))
TOKEN = os.getenv("TOKEN", "")
ARGO_AUTH = os.getenv("ARGO_AUTH", "")
ARGO_DOMAIN = os.getenv("ARGO_DOMAIN", "")
CUSTOM_DNS = os.getenv("CUSTOM_DNS", "")
ECH_LOG = os.getenv("ECH_LOG", "ech.log")
ARGO_LOG = os.getenv("ARGO_LOG", "argo.log")

ECH_BIN = "./ech-server"
CLOUDFLARED_BIN = "./cloudflared"

# ---------------- Utils ---------------- #
def detect_arch():
    arch = platform.machine().lower()
    if arch in ("x86_64", "amd64"):
        return ("https://www.baipiao.eu.org/ech/ech-server-linux-amd64",
                "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64")
    elif arch in ("i386", "i686"):
        return ("https://www.baipiao.eu.org/ech/ech-server-linux-386",
                "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-386")
    elif arch in ("aarch64", "arm64"):
        return ("https://www.baipiao.eu.org/ech/ech-server-linux-arm64",
                "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64")
    else:
        print(f"❌ Unsupported architecture: {arch}")
        exit(1)

def download_binaries():
    ech_url, cf_url = detect_arch()
    if not os.path.exists(ECH_BIN):
        print("🔽 Downloading ech-server binary...")
        subprocess.run(["curl", "-L", ech_url, "-o", ECH_BIN], check=True)
    if not os.path.exists(CLOUDFLARED_BIN):
        print("🔽 Downloading cloudflared binary...")
        subprocess.run(["curl", "-L", cf_url, "-o", CLOUDFLARED_BIN], check=True)
    os.chmod(ECH_BIN, 0o755)
    os.chmod(CLOUDFLARED_BIN, 0o755)

# ---------------- HTTP Service ---------------- #
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Hello World!\n")
        else:
            self.send_error(404)

def start_http():
    server = HTTPServer(("0.0.0.0", PORT), RequestHandler)
    print(f"🌍 HTTP service running at: http://0.0.0.0:{PORT}")
    server.serve_forever()

# ---------------- ECH Server ---------------- #
def start_ech():
    cmd = [ECH_BIN, "-l", f"ws://0.0.0.0:{WSPORT}"]
    if TOKEN:
        cmd += ["-token", TOKEN]
    if CUSTOM_DNS:
        cmd += ["--dns", CUSTOM_DNS]

    print(f"🔌 Starting ECH WebSocket on port {WSPORT}…")
    with open(ECH_LOG, "a") as f:
        subprocess.Popen(cmd, stdout=f, stderr=f)

# ---------------- Cloudflared ---------------- #
def start_cloudflared():
    url = f"http://localhost:{WSPORT}"
    cmd = [CLOUDFLARED_BIN, "tunnel", "--protocol", "http2", "--url", url]

    if CUSTOM_DNS:
        cmd += ["--resolver", CUSTOM_DNS]

    if ARGO_AUTH and ARGO_DOMAIN:
        cmd += ["run", "--token", ARGO_AUTH]
        print(f"☁ Using custom domain: {ARGO_DOMAIN}")
    else:
        cmd += ["--logfile", ARGO_LOG, "--loglevel", "info"]
        print("☁ Using temporary Cloudflare tunnel…")

    subprocess.Popen(cmd, stdout=open(os.devnull, "w"), stderr=open(ARGO_LOG, "a"))

# ---------------- Weekly Log Cleanup & Restart ---------------- #
def weekly_restart():
    tz = pytz.timezone("Asia/Shanghai")
    now = datetime.now(tz)
    print(f"♻ {now} Weekly maintenance: cleaning logs and restarting services…")
    for f in (ECH_LOG, ARGO_LOG):
        if os.path.exists(f):
            os.remove(f)
    os.execv("/usr/bin/python3", ["python3", "app.py"])

def schedule_task():
    schedule.every().monday.at("03:00").do(weekly_restart)
    while True:
        schedule.run_pending()
        time.sleep(1)

# ---------------- Main ---------------- #
def main():
    print("🚀 Starting services…")
    download_binaries()
    threading.Thread(target=start_http, daemon=True).start()
    start_ech()
    start_cloudflared()
    threading.Thread(target=schedule_task, daemon=True).start()
    print("🎉 All services are running successfully!")
    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()
