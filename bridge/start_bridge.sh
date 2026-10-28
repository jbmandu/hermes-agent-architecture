#!/bin/bash
# Inicia a ponte MCP e o tunel ngrok (dominio fixo). Idempotente.
set -a; . /opt/data/.env; set +a
LOG=/opt/data/logs
pkill -f mcp_bridge.py 2>/dev/null; pkill -f "ngrok http" 2>/dev/null; sleep 1
nohup /opt/data/venvs/mcp_bridge/bin/python /opt/data/scripts/mcp_bridge.py > $LOG/mcp_bridge.log 2>&1 &
sleep 3
/opt/data/bin/ngrok config add-authtoken "$NGROK_AUTHTOKEN" --config /opt/data/ngrok.yml >/dev/null
nohup /opt/data/bin/ngrok http --config /opt/data/ngrok.yml --url="https://$BRIDGE_PUBLIC_HOST" ${CLAUDE_BRIDGE_PORT:-8765} --log=stdout > $LOG/ngrok.log 2>&1 &
sleep 5
echo "bridge pid: $(pgrep -f mcp_bridge.py)"; echo "ngrok pid: $(pgrep -f 'ngrok http')"
