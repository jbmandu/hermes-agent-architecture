"""Ponte MCP (experimental) (streamable HTTP) para apps de IA (Claude, ChatGPT) falarem com o Hermes.
Ferramenta perguntar_hermes -> API local do Hermes.
Seguranca: cada cliente tem caminho secreto proprio + filtro de IP de origem
(X-Forwarded-For do ngrok); o Claude tambem exige o cabecalho X-Hermes-Key.
.env: API_SERVER_KEY, CLAUDE_BRIDGE_PATH, CLAUDE_BRIDGE_KEY, CHATGPT_BRIDGE_PATH (opcional),
CLAUDE_BRIDGE_PORT (8765).
"""
import os, json, ipaddress, hmac, urllib.request, time

def load_env(path="/opt/data/.env"):
    try:
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass

load_env()
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
import uvicorn

KEY = os.environ["API_SERVER_KEY"]
PORT = int(os.environ.get("CLAUDE_BRIDGE_PORT", "8765"))
API = "http://127.0.0.1:8642/v1/chat/completions"
HOST = os.environ["BRIDGE_PUBLIC_HOST"]  # ex.: seu-dominio.ngrok-free.dev
LOG = os.environ.get("BRIDGE_LOG", "/opt/data/logs/mcp_bridge_access.log")

ANTHROPIC = [ipaddress.ip_network("160.79.104.0/21"), ipaddress.ip_network("2607:6bc0::/48")]
OPENAI_CACHE = os.environ.get("BRIDGE_OPENAI_CACHE", "/opt/data/scripts/openai_connector_ips.json")

def openai_nets():
    data = None
    try:
        req = urllib.request.Request("https://openai.com/chatgpt-connectors.json",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r)
        json.dump(data, open(OPENAI_CACHE, "w"))
    except Exception:
        try:
            data = json.load(open(OPENAI_CACHE))
        except Exception:
            data = {"prefixes": []}
    nets = []
    for p in data.get("prefixes", []):
        v = p.get("ipv4Prefix") or p.get("ipv6Prefix")
        if v:
            nets.append(ipaddress.ip_network(v))
    return nets

CLIENTS = {}
if os.environ.get("CLAUDE_BRIDGE_PATH"):
    CLIENTS[os.environ["CLAUDE_BRIDGE_PATH"].strip("/")] = {
        "name": "claude", "nets": ANTHROPIC, "key": os.environ.get("CLAUDE_BRIDGE_KEY")}
if os.environ.get("CHATGPT_BRIDGE_PATH"):
    CLIENTS[os.environ["CHATGPT_BRIDGE_PATH"].strip("/")] = {
        "name": "chatgpt", "nets": openai_nets(), "key": None}

mcp = FastMCP("Hermes", streamable_http_path="/mcp", stateless_http=True,
              transport_security=TransportSecuritySettings(
                  enable_dns_rebinding_protection=True,
                  allowed_hosts=[HOST, "127.0.0.1:*", "localhost:*"],
                  allowed_origins=["https://claude.ai", "https://chatgpt.com", f"https://{HOST}"]))

@mcp.tool()
def perguntar_hermes(mensagem: str) -> str:
    """Envia uma mensagem ao agente Hermes (com acesso aos sistemas da empresa) e
    devolve a resposta. Use para perguntas sobre vendas, visitacao, lojistas,
    indicadores de qualidade ou tarefas do agente. Cada chamada e uma conversa nova:
    inclua todo o contexto necessario."""
    body = json.dumps({"model": "hermes-agent", "stream": False,
        "messages": [{"role": "user", "content": "Mensagem do dono via app de IA: " + mensagem}]}).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            d = json.load(r)
        return d["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erro ao falar com o Hermes: {e}"

inner = mcp.streamable_http_app()

def log(msg):
    try:
        with open(LOG, "a") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")
    except Exception:
        pass

async def deny(send, code=404):
    await send({"type": "http.response.start", "status": code,
                "headers": [(b"content-type", b"text/plain")]})
    await send({"type": "http.response.body", "body": b"Not Found"})

async def app(scope, receive, send):
    if scope["type"] != "http":
        return await inner(scope, receive, send)
    path = scope.get("path", "")
    parts = path.strip("/").split("/")
    headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
    xff = headers.get("x-forwarded-for", "")
    ip_s = xff.split(",")[0].strip() if xff else (scope.get("client") or ("", 0))[0]
    if len(parts) != 2 or parts[1] != "mcp" or parts[0] not in CLIENTS:
        log(f"404 path ip={ip_s}")
        return await deny(send)
    c = CLIENTS[parts[0]]
    local_test = not xff and ip_s == "127.0.0.1"
    try:
        ip = ipaddress.ip_address(ip_s)
        ip_ok = local_test or any(ip in n for n in c["nets"])
    except ValueError:
        ip_ok = False
    key_ok = c["key"] is None or hmac.compare_digest(headers.get("x-hermes-key", ""), c["key"])
    if not (ip_ok and key_ok):
        log(f"403 {c['name']} ip={ip_s} ip_ok={ip_ok} key_ok={key_ok}")
        return await deny(send)
    log(f"200 {c['name']} ip={ip_s}")
    scope = dict(scope, path="/mcp", raw_path=b"/mcp")
    return await inner(scope, receive, send)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT, proxy_headers=False)
