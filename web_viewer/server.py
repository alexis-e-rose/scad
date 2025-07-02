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
            
            # Import and use the CAD automation system
            import sys
            sys.path.append('/workspaces/scad')
            from cad_automator import NucDeckCADAutomator
            
            # Create automator instance and apply parameters
            automator = NucDeckCADAutomator()
            
            # Convert web parameters to CAD parameters
            cad_params = {}
            if 'phoneWidth' in parameters:
                cad_params['phone_width'] = parameters['phoneWidth']
            if 'phoneHeight' in parameters:
                cad_params['phone_height'] = parameters['phoneHeight']
            if 'batterySize' in parameters:
                cad_params['battery_height'] = parameters['batterySize'] / 1000  # Convert mAh to rough height
            if 'gripOffset' in parameters:
                cad_params['grip_offset'] = parameters['gripOffset']
            
            # Generate STL with new parameters
            output_stl = "/workspaces/scad/output/nucdeck_web_generated.stl"
            success = automator.render_stl(
                str(automator.main_scad_file), 
                output_stl, 
                cad_params
            )
            
            response = {
                "status": "success" if success else "error",
                "message": "Model regenerated successfully" if success else "Failed to regenerate model",
                "parameters": parameters,
                "output_file": output_stl if success else None,
                "cad_params": cad_params
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                "status": "error",
                "message": f"Error processing request: {str(e)}",
                "parameters": parameters if 'parameters' in locals() else {}
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
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
    
    def do_GET(self):
        """Handle GET requests with custom routing"""
        if self.path.startswith('/output/'):
            # Serve files from the output directory
            file_path = '/workspaces/scad' + self.path
            if os.path.exists(file_path):
                self.send_response(200)
                if self.path.endswith('.stl'):
                    self.send_header('Content-type', 'application/octet-stream')
                    self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
                else:
                    self.send_header('Content-type', 'application/octet-stream')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")
        else:
            # Use default handler for other requests
            super().do_GET()

def start_server(port=8000):
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
    parser.add_argument('--port', type=int, default=8000, help='Port to serve on (default: 8000)')
    args = parser.parse_args()
    
    start_server(args.port)
