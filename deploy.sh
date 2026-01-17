#!/bin/bash
# deploy.sh: Déploiement ear-to-code sur pwnd.icu
# Les IAs codent, on aide

set -e

DOMAIN="pwnd.icu"
PORT=80
USER=$(whoami)
DIR=$(pwd)

echo "=== Déploiement ear-to-code ==="
echo "Domain: $DOMAIN"
echo "User: $USER"
echo "Dir: $DIR"

# 1. Service systemd
echo "[1/4] Création service systemd..."
sudo tee /etc/systemd/system/ear-to-code.service > /dev/null << EOF
[Unit]
Description=ear-to-code web server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$DIR
ExecStart=/usr/bin/python3 $DIR/web/server.py $PORT
Restart=always
RestartSec=5
Environment=PORT=$PORT

[Install]
WantedBy=multi-user.target
EOF

# 2. Firewall
echo "[2/4] Configuration firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    echo "UFW: ports 80,443 ouverts"
elif command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    sudo firewall-cmd --reload
    echo "firewalld: http/https ouverts"
else
    echo "Pas de firewall détecté (ou iptables manuel)"
fi

# 3. Activer et démarrer
echo "[3/4] Activation service..."
sudo systemctl daemon-reload
sudo systemctl enable ear-to-code
sudo systemctl start ear-to-code
sudo systemctl status ear-to-code --no-pager

# 4. Instructions DNS
echo ""
echo "=== [4/4] Configuration DNS sur Hetzner ==="
IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
echo ""
echo "Sur Hetzner DNS Console:"
echo "  Type: A"
echo "  Name: @"
echo "  Value: $IP"
echo ""
echo "  Type: A"
echo "  Name: www"
echo "  Value: $IP"
echo ""
echo "Attends 5-10 min pour propagation DNS."
echo ""
echo "Test: curl http://$DOMAIN"
echo ""
echo "=== HTTPS (optionnel) ==="
echo "sudo apt install certbot"
echo "sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN"
echo ""
echo "Done. Les IAs sont en ligne."
