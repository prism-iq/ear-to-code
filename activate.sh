#!/bin/bash
# Ear-to-Code Activation - Part of Pantheon

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export EAR_ROOT="$SCRIPT_DIR"

case "${1:-start}" in
    start)
        python3 "$SCRIPT_DIR/senses.py" &
        echo "[+] Ear senses started (PID: $!)"
        ;;
    cam)
        python3 "$SCRIPT_DIR/cam_sense.py" &
        echo "[+] Camera sense started (PID: $!)"
        ;;
    stop)
        pkill -f "senses.py|cam_sense.py"
        echo "[*] Ear stopped"
        ;;
    status)
        pgrep -f "senses.py|cam_sense.py" && echo "[+] Ear running" || echo "[-] Ear not running"
        ;;
    *)
        echo "Usage: $0 {start|cam|stop|status}"
        ;;
esac
