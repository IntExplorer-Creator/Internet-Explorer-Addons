# IntExplorerExtensions_Gateway.py — Финальный прототип с HTTPS и 0.0.0.0
import http.server
import socketserver
import urllib.request
import socket
import select

PORT = 8080
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:153.0) Gecko/20100101 Firefox/153.0"

class IERetroHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        req = urllib.request.Request(self.path, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                for key, value in response.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_error(500, f"IntExplorerExtensions Error: {e}")

    def do_CONNECT(self):
        # Туннелирование для HTTPS-соединений
        try:
            host, port = self.path.split(':')
            port = int(port)
        except ValueError:
            host = self.path
            port = 443

        try:
            with socket.create_connection((host, port)) as sock:
                self.send_response(200, "Connection Established")
                self.end_headers()
                
                conns = [self.connection, sock]
                while True:
                    r, w, ex = select.select(conns, [], conns, 1)
                    if ex:
                        break
                    if r:
                        for r_sock in r:
                            other = sock if r_sock is self.connection else self.connection
                            data = r_sock.recv(8192)
                            if not data:
                                return
                            other.sendall(data)
        except Exception as e:
            self.send_error(500, f"Tunnel Error: {e}")

print(f"[IntExplorerExtensions] Шлюз запущен на 0.0.0.0:{PORT}")
with socketserver.TCPServer(("0.0.0.0", PORT), IERetroHandler) as httpd:
    httpd.serve_forever()
