#!/usr/bin/env python3
"""
Simple HTTP server for the NucDeck STL viewer
Serves the web interface and provides API endpoints for CAD automation
"""

import http.server
import socketserver
import json
import os
from pathlib import Path
import threading
import webbrowser
from urllib.parse import urlparse, parse_qs

class NucDeckHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        super().__init__(*args, directory="/workspaces/scad/web_viewer", **kwargs)
    
    def do_POST(self):
        """Handle POST requests for API endpoints"""
        if self.path == '/api/regenerate':
            self.handle_regenerate_request()
        elif self.path == '/api/upload':
            self.handle_file_upload()
        else:
            self.send_error(404, "API endpoint not found")
    
    def handle_regenerate_request(self):
        """Handle model regeneration requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            parameters = json.loads(post_data.decode('utf-8'))
            
            # Here you would call the CAD automation script
            # For now, just return a success response
            response = {
                "status": "success",
                "message": "Model regeneration initiated",
                "parameters": parameters
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"Error processing request: {str(e)}")
    
    def handle_file_upload(self):
        """Handle STL file uploads"""
        # Implementation for file upload handling
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {"status": "success", "message": "File upload handled"}
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def start_server(port=8080):
    """Start the HTTP server"""
    try:
        with socketserver.TCPServer(("", port), NucDeckHTTPHandler) as httpd:
            print(f"🚀 NucDeck STL Viewer server starting on port {port}")
            print(f"🌐 Open your browser to: http://localhost:{port}")
            print("📁 Serving files from: /workspaces/scad/web_viewer")
            print("⚡ Press Ctrl+C to stop the server")
            
            # Automatically open browser
            def open_browser():
                webbrowser.open(f'http://localhost:{port}')
            
            timer = threading.Timer(1.0, open_browser)
            timer.start()
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Port {port} is already in use. Try a different port.")
            print(f"   You can specify a different port: python server.py --port 8081")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='NucDeck STL Viewer Server')
    parser.add_argument('--port', type=int, default=8080, help='Port to serve on (default: 8080)')
    args = parser.parse_args()
    
    start_server(args.port)
