"""
HTTP Server with Custom Routes
Build a lightweight HTTP server with routing, middleware, and error handling
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from typing import Dict, Callable, Tuple, Optional
from urllib.parse import urlparse, parse_qs
import logging
from datetime import datetime
import mimetypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Router:
    """Simple URL router"""

    def __init__(self):
        """Initialize router"""
        self.routes: Dict[str, Dict[str, Callable]] = {}
        self.middleware: list = []

    def add_route(self, path: str, method: str, handler: Callable) -> None:
        """Add route"""
        if path not in self.routes:
            self.routes[path] = {}
        
        self.routes[path][method] = handler
        logger.info(f"✅ Route added: {method} {path}")

    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware"""
        self.middleware.append(middleware)

    def get_route(self, path: str, method: str) -> Optional[Callable]:
        """Get route handler"""
        return self.routes.get(path, {}).get(method)

    def apply_middleware(self, request: 'HTTPRequest') -> Optional[Tuple[int, str, str]]:
        """Apply middleware stack"""
        for mw in self.middleware:
            result = mw(request)
            if result:  # Middleware can return early response
                return result
        return None


class HTTPRequest:
    """Request object"""

    def __init__(self, method: str, path: str, headers: Dict, body: str = ""):
        """Initialize request"""
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self.query_params = self._parse_query()

    def _parse_query(self) -> Dict:
        """Parse query parameters"""
        parsed = urlparse(self.path)
        return parse_qs(parsed.query)


class CustomHTTPHandler(BaseHTTPRequestHandler):
    """Custom HTTP request handler"""

    router = Router()

    def do_GET(self):
        """Handle GET requests"""
        self.handle_request('GET')

    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        self.handle_request('POST', body)

    def do_PUT(self):
        """Handle PUT requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        self.handle_request('PUT', body)

    def do_DELETE(self):
        """Handle DELETE requests"""
        self.handle_request('DELETE')

    def handle_request(self, method: str, body: str = "") -> None:
        """Handle request"""
        path = self.path.split('?')[0]  # Remove query string
        
        request = HTTPRequest(
            method=method,
            path=self.path,
            headers=dict(self.headers),
            body=body
        )

        # Check middleware
        middleware_response = self.router.apply_middleware(request)
        if middleware_response:
            status, content_type, response = middleware_response
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(response.encode())
            return

        # Get route handler
        handler = self.router.get_route(path, method)

        if handler:
            try:
                status, content_type, response = handler(request)
                self.send_response(status)
                self.send_header('Content-Type', content_type)
                self.end_headers()
                self.wfile.write(response.encode())
                logger.info(f"✅ {method} {path} - {status}")
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


class SimpleHTTPServer:
    """Simple HTTP server"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        """Initialize server"""
        self.host = host
        self.port = port
        self.router = Router()

    def add_route(self, path: str, method: str, handler: Callable) -> None:
        """Add route"""
        self.router.add_route(path, method, handler)

    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware"""
        self.router.add_middleware(middleware)

    def run(self) -> None:
        """Run server"""
        CustomHTTPHandler.router = self.router
        server = HTTPServer((self.host, self.port), CustomHTTPHandler)
        logger.info(f"🚀 Server running on {self.host}:{self.port}")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("⏹️  Server stopped")
            server.shutdown()


def demo_server():
    """Demo HTTP server"""
    server = SimpleHTTPServer(port=8888)

    # Define handlers
    def health(request: HTTPRequest) -> Tuple[int, str, str]:
        """Health check"""
        return 200, "application/json", json.dumps({"status": "ok"})

    def hello(request: HTTPRequest) -> Tuple[int, str, str]:
        """Hello endpoint"""
        name = request.query_params.get('name', ['World'])[0]
        return 200, "text/plain", f"Hello, {name}!"

    def json_data(request: HTTPRequest) -> Tuple[int, str, str]:
        """Return JSON"""
        data = {
            "message": "Success",
            "timestamp": datetime.now().isoformat()
        }
        return 200, "application/json", json.dumps(data)

    def not_found(request: HTTPRequest) -> Tuple[int, str, str]:
        """404 handler"""
        return 404, "application/json", json.dumps({"error": "Not Found"})

    # Add auth middleware
    def auth_middleware(request: HTTPRequest) -> Optional[Tuple[int, str, str]]:
        """Check authorization"""
        if request.path.startswith('/admin'):
            token = request.headers.get('Authorization')
            if not token or token != "Bearer secret-key":
                return 401, "application/json", json.dumps({"error": "Unauthorized"})
        return None

    # Register routes
    server.add_route('/health', 'GET', health)
    server.add_route('/hello', 'GET', hello)
    server.add_route('/api/data', 'GET', json_data)
    
    # Add middleware
    server.add_middleware(auth_middleware)

    print("\n🌐 HTTP Server\n")
    print("Endpoints:")
    print("  GET  /health")
    print("  GET  /hello?name=Alice")
    print("  GET  /api/data")
    
    # server.run()


if __name__ == "__main__":
    print("🌐 HTTP Server with Custom Routes\n")
    print("Features:")
    print("✓ URL routing")
    print("✓ Middleware support")
    print("✓ Multiple HTTP methods")
    print("✓ JSON responses")
    print("✓ Error handling")
