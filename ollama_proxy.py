#!/usr/bin/env python3
"""
Simple CORS proxy for Ollama to fix browser access issues.
Run this before opening the dashboard in browser.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.error
from urllib.parse import urljoin

OLLAMA_URL = "http://localhost:11434"

class OllamaCORSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests and proxy to Ollama with CORS headers"""
        try:
            content_length = int(self.headers.get('content-length', 0))
            body = self.rfile.read(content_length)
            
            # Extract the path and route to Ollama
            target_url = urljoin(OLLAMA_URL, self.path)
            
            # Forward request to Ollama
            req = urllib.request.Request(
                target_url,
                data=body,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            with urllib.request.urlopen(req) as response:
                response_data = response.read()
                
                # Send response with CORS headers
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, api-key')
                self.end_headers()
                self.wfile.write(response_data)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_GET(self):
        """Handle GET requests and proxy to Ollama with CORS headers"""
        try:
            target_url = urljoin(OLLAMA_URL, self.path)
            
            # Forward request to Ollama
            with urllib.request.urlopen(target_url) as response:
                response_data = response.read()
                
                # Send response with CORS headers
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, api-key')
                self.end_headers()
                self.wfile.write(response_data)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        """Handle preflight OPTIONS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, api-key')
        self.send_header('Content-Length', '0')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        print(f"[Proxy] {format % args}")

if __name__ == '__main__':
    PORT = 8899
    handler = OllamaCORSHandler
    server = HTTPServer(('127.0.0.1', PORT), handler)
    print(f"🔄 Ollama CORS Proxy running on http://127.0.0.1:{PORT}")
    print(f"📍 Proxying to: {OLLAMA_URL}")
    print(f"💡 Update AI Endpoint in dashboard to: http://127.0.0.1:{PORT}/v1/chat/completions")
    print(f"✋ Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Proxy stopped")
