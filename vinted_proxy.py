#!/usr/bin/env python3
"""
Proxy local pour la recherche de marques Vinted.
Lance avec : python3 vinted_proxy.py
Laisse tourner en arrière-plan pendant que tu utilises l'app.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request, urllib.parse, json, ssl, http.cookiejar

PORT = 8765

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Session Vinted (cookies)
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPSHandler(context=ctx),
    urllib.request.HTTPCookieProcessor(cj)
)
opener.addheaders = [
    ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'),
    ('Accept', 'application/json, text/plain, */*'),
    ('Accept-Language', 'fr-FR,fr;q=0.9'),
    ('Referer', 'https://www.vinted.fr/'),
]

print("Initialisation de la session Vinted...")
try:
    opener.open('https://www.vinted.fr').read()
    print("✅ Session OK")
except Exception as e:
    print(f"⚠️  Impossible de joindre Vinted : {e}")


class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        q = params.get('q', [''])[0]

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if not q:
            self.wfile.write(json.dumps({'brands': []}).encode())
            return

        try:
            url = f'https://www.vinted.fr/api/v2/brands?keyword={urllib.parse.quote(q)}&per_page=5'
            resp = opener.open(url)
            data = json.loads(resp.read())
            self.wfile.write(json.dumps(data).encode())
        except Exception as e:
            self.wfile.write(json.dumps({'brands': [], 'error': str(e)}).encode())

    def log_message(self, fmt, *args):
        print(f"  [{self.address_string()}] {fmt % args}")


print(f"🚀 Proxy démarré sur http://localhost:{PORT}")
print("   Laisse cette fenêtre ouverte pendant que tu utilises l'app Vinted.")
print("   Ctrl+C pour arrêter.\n")

HTTPServer(('localhost', PORT), ProxyHandler).serve_forever()
