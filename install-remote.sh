#!/bin/bash
# ONE-SHOT: Colle ça sur un serveur Ubuntu fresh
# curl -sL https://pwnd.icu/install.sh | bash
# ou copie-colle direct

set -e

echo "=== ear-to-code install ==="

# 1. Packages
apt update && apt install -y python3 python3-pip git curl

# 2. Code
cd /root
git clone https://github.com/mmusic/ear-to-code.git 2>/dev/null || true
cd ear-to-code

# Si pas de git, on crée minimal
mkdir -p web organs logs confrontations

# 3. Serveur web minimal
cat > web/server.py << 'PYEOF'
#!/usr/bin/env python3
import http.server, socketserver, json, os
from pathlib import Path
from urllib.parse import urlparse

PORT = int(os.environ.get("PORT", 80))
BASE = Path(__file__).parent.parent

class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        p = urlparse(self.path).path
        if p == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>ear-to-code</title>
<style>body{background:#0a0a0f;color:#0f8;font-family:monospace;padding:40px;}</style></head>
<body><h1>ear-to-code</h1><p>IAs pensent localement. Pas de perfusion.</p>
<p>Entites: nyx, cipher, flow</p>
<p>Quantum: variables en superposition</p>
<p><a href="/api/status" style="color:#0cf">/api/status</a></p></body></html>""")
        elif p == "/api/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status":"online","entities":["nyx","cipher","flow"]}).encode())
        else:
            self.send_error(404)

with socketserver.TCPServer(("", PORT), H) as httpd:
    print(f"[web] http://0.0.0.0:{PORT}")
    httpd.serve_forever()
PYEOF

# 4. Service systemd
cat > /etc/systemd/system/ear-to-code.service << EOF
[Unit]
Description=ear-to-code
After=network.target

[Service]
Type=simple
WorkingDirectory=/root/ear-to-code
ExecStart=/usr/bin/python3 /root/ear-to-code/web/server.py
Restart=always
Environment=PORT=80

[Install]
WantedBy=multi-user.target
EOF

# 5. Firewall
ufw allow 80/tcp 2>/dev/null || true
ufw allow 443/tcp 2>/dev/null || true

# 6. Start
systemctl daemon-reload
systemctl enable ear-to-code
systemctl start ear-to-code

# 7. Done
IP=$(curl -s ifconfig.me)
echo ""
echo "=== DONE ==="
echo "Site: http://$IP"
echo ""
echo "DNS: Ajoute A record pwnd.icu -> $IP"
echo ""
echo "Les IAs sont en ligne."
