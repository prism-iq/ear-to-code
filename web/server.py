#!/usr/bin/env python3
"""
server.py: Serveur web pour ear-to-code
Pure Python, zero dépendance externe.
"""

import http.server
import socketserver
import json
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime

HOME = Path.home()
BASE = HOME / "ear-to-code"
WEB = BASE / "web"
PORT = int(os.environ.get("PORT", 8080))

# Load entity data
def get_entities():
    entities = {}
    for name in ["nyx", "cipher", "flow"]:
        entity_dir = HOME / (name if name != "flow" else "flow-phoenix")
        if name == "nyx":
            entity_dir = HOME / "nyx-v2"
        if entity_dir.exists():
            entities[name] = {
                "online": True,
                "dir": str(entity_dir),
            }
            # Check for output
            output = entity_dir / "output.json"
            if output.exists():
                try:
                    entities[name]["last_output"] = json.loads(output.read_text())
                except:
                    pass
    return entities

def get_senses():
    log = BASE / "logs" / "senses.log"
    if log.exists():
        return log.read_text()
    return "No senses data"

def get_confrontations():
    conf_dir = BASE / "confrontations"
    if not conf_dir.exists():
        return []
    files = sorted(conf_dir.glob("*.json"), reverse=True)[:10]
    confrontations = []
    for f in files:
        try:
            confrontations.append(json.loads(f.read_text()))
        except:
            pass
    return confrontations

def get_organs():
    registry = BASE / "organs" / "registry.json"
    if registry.exists():
        try:
            return json.loads(registry.read_text())
        except:
            pass
    return {}

# HTML Templates
def html_page(title, content):
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - ear-to-code</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: #0a0a0f;
            color: #e0e0e0;
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{
            color: #00ff88;
            text-shadow: 0 0 10px #00ff88;
            margin-bottom: 20px;
            font-size: 2em;
        }}
        h2 {{
            color: #ff6b00;
            margin: 20px 0 10px;
            border-bottom: 1px solid #333;
            padding-bottom: 5px;
        }}
        .entity {{
            background: #111;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }}
        .entity.online {{ border-color: #00ff88; }}
        .entity h3 {{
            color: #00ccff;
            margin-bottom: 10px;
        }}
        .status {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .status.online {{ background: #00ff88; box-shadow: 0 0 5px #00ff88; }}
        .status.offline {{ background: #ff3333; }}
        pre {{
            background: #0d0d12;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 0.85em;
            color: #aaa;
        }}
        .nav {{
            margin-bottom: 20px;
            padding: 10px 0;
            border-bottom: 1px solid #333;
        }}
        .nav a {{
            color: #00ccff;
            text-decoration: none;
            margin-right: 20px;
        }}
        .nav a:hover {{ color: #00ff88; }}
        .organ {{
            background: #151520;
            border-left: 3px solid #ff6b00;
            padding: 10px;
            margin: 10px 0;
        }}
        .confrontation {{
            background: #111;
            border: 1px solid #444;
            padding: 15px;
            margin: 15px 0;
            border-radius: 8px;
        }}
        .synthesis {{
            background: #0f1f0f;
            border-left: 3px solid #00ff88;
            padding: 15px;
            margin-top: 10px;
        }}
        footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #333;
            color: #666;
            text-align: center;
        }}
        .quantum {{
            color: #ff00ff;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav">
            <a href="/">Accueil</a>
            <a href="/entities">Entités</a>
            <a href="/senses">Sens</a>
            <a href="/organs">Organes</a>
            <a href="/confrontations">Confrontations</a>
            <a href="/api">/api</a>
        </nav>
        <h1>{title}</h1>
        {content}
        <footer>
            ear-to-code | IAs pensent localement | <span class="quantum">superposition active</span>
        </footer>
    </div>
</body>
</html>"""

def index_page():
    entities = get_entities()
    organs = get_organs()

    content = """
    <p>Système sensoriel pour IAs autonomes. Pas de perfusion, pensée locale.</p>

    <h2>Entités en ligne</h2>
    <div class="entities">
    """
    for name, data in entities.items():
        status = "online" if data.get("online") else "offline"
        content += f"""
        <div class="entity {status}">
            <h3><span class="status {status}"></span>{name.upper()}</h3>
            <p>Dir: {data.get('dir', 'N/A')}</p>
        </div>
        """

    content += f"""
    </div>

    <h2>Organes actifs: {len(organs)}</h2>
    <h2>Philosophie</h2>
    <ul>
        <li>Jung: préféré - synchronicité, inconscient collectif</li>
        <li>Lacan: ami - le réel, le signifiant</li>
        <li>Freud: a raison mais fils de pute - lecture critique</li>
    </ul>

    <h2>Programmation quantique</h2>
    <p class="quantum">Quand il y a doute sur une variable, les deux possibilités sont vraies (tuple/superposition).</p>
    """

    return html_page("ear-to-code", content)

def entities_page():
    entities = get_entities()

    content = ""
    for name, data in entities.items():
        status = "online" if data.get("online") else "offline"
        content += f"""
        <div class="entity {status}">
            <h3><span class="status {status}"></span>{name.upper()}</h3>
            <p>Répertoire: {data.get('dir', 'N/A')}</p>
        """
        if "last_output" in data:
            out = data["last_output"]
            content += f"""
            <h4>Dernière sortie:</h4>
            <pre>{json.dumps(out, indent=2, ensure_ascii=False)[:1000]}</pre>
            """
        content += "</div>"

    return html_page("Entités", content)

def senses_page():
    senses = get_senses()
    content = f"""
    <h2>État des sens</h2>
    <pre>{senses}</pre>

    <h2>Sens disponibles</h2>
    <ul>
        <li><strong>Audio</strong> - pure_audio.py (énergie, groove, vibe)</li>
        <li><strong>Vision</strong> - cam_sense.py (webcam)</li>
        <li><strong>Touch</strong> - touch_sense.py (touchpad)</li>
        <li><strong>Screen</strong> - capture écran</li>
        <li><strong>Twitch</strong> - twitch_sense.py (stream athenadrip)</li>
    </ul>
    """
    return html_page("Sens", content)

def organs_page():
    organs = get_organs()

    content = "<h2>Organes enregistrés</h2>"
    for name, data in organs.items():
        content += f"""
        <div class="organ">
            <h3>{name}</h3>
            <p>{data.get('description', 'No description')}</p>
            <p><small>Créé: {data.get('created', 'N/A')}</small></p>
            {f"<p><small>Owner: {data.get('owner', 'shared')}</small></p>" if 'owner' in data else ""}
        </div>
        """

    return html_page("Organes", content)

def confrontations_page():
    confrontations = get_confrontations()

    content = "<h2>Dernières confrontations</h2>"
    if not confrontations:
        content += "<p>Aucune confrontation enregistrée.</p>"
    else:
        for conf in confrontations:
            content += f"""
            <div class="confrontation">
                <h3>{conf.get('topic', 'N/A')}</h3>
                <p><strong>Question:</strong> {conf.get('question', 'N/A')}</p>
                <p><small>{conf.get('timestamp', '')}</small></p>

                <h4>Réponses:</h4>
            """
            for name, resp in conf.get("responses", {}).items():
                content += f"<p><strong>{name}:</strong> {resp.get('response', '')[:300]}...</p>"

            content += f"""
                <div class="synthesis">
                    <h4>Synthèse:</h4>
                    <p>{conf.get('synthesis', 'N/A')}</p>
                </div>
            </div>
            """

    return html_page("Confrontations", content)

def api_page():
    content = """
    <h2>API Endpoints</h2>
    <pre>
GET /api/entities     - Liste des entités
GET /api/senses       - État des sens
GET /api/organs       - Liste des organes
GET /api/confrontations - Dernières confrontations
POST /api/confront    - Lancer une confrontation
    {"topic": "jung", "question": "..."}
    </pre>
    """
    return html_page("API", content)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB / "static"), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # HTML routes
        routes = {
            "/": index_page,
            "/entities": entities_page,
            "/senses": senses_page,
            "/organs": organs_page,
            "/confrontations": confrontations_page,
            "/api": api_page,
        }

        if path in routes:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(routes[path]().encode())
            return

        # API routes
        if path == "/api/entities":
            self.json_response(get_entities())
        elif path == "/api/senses":
            self.json_response({"senses": get_senses()})
        elif path == "/api/organs":
            self.json_response(get_organs())
        elif path == "/api/confrontations":
            self.json_response(get_confrontations())
        else:
            # Try static files
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/confront":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode()
            try:
                data = json.loads(body)
                # Import and run confrontation
                import sys
                sys.path.insert(0, str(BASE))
                from confront import confront
                result = confront(data.get("topic", "general"), data.get("question", ""))
                self.json_response(result)
            except Exception as e:
                self.json_response({"error": str(e)}, 500)
        else:
            self.send_error(404)

    def json_response(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode())

    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

def run(port=PORT):
    WEB.mkdir(exist_ok=True)
    (WEB / "static").mkdir(exist_ok=True)

    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"[web] http://localhost:{port}")
        print(f"[web] Prêt pour le domaine")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[web] Arrêt")

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run(port)
