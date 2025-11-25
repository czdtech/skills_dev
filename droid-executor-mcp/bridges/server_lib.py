import http.server
import json
import logging
import sys
from typing import Any, Callable, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("BridgeServer")


class BridgeRequestHandler(http.server.BaseHTTPRequestHandler):
    """Base request handler for Bridge servers."""

    # To be overridden by subclasses or set by the factory
    handler_func: Callable[[Dict[str, Any]], Dict[str, Any]] | None = None
    endpoint: str = "/"

    def do_POST(self):
        if self.path != self.endpoint:
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self.send_error(400, "Missing Content-Length")
            return

        try:
            body = self.rfile.read(content_length)
            payload = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        try:
            if self.handler_func:
                # Access via class to avoid binding 'self' if it's a plain function
                response = self.__class__.handler_func(payload)
            else:
                response = {"error": "No handler function defined"}
                
            response_bytes = json.dumps(response).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response_bytes)))
            self.end_headers()
            self.wfile.write(response_bytes)
            
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def log_message(self, format, *args):
        # Override to use our logger
        logger.info("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), format % args))


def run_server(port: int, endpoint: str, handler_func: Callable[[Dict[str, Any]], Dict[str, Any]]):
    """Starts a bridge server."""
    
    class RequestHandler(BridgeRequestHandler):
        pass
    
    RequestHandler.endpoint = endpoint
    RequestHandler.handler_func = handler_func

    server_address = ("", port)
    httpd = http.server.HTTPServer(server_address, RequestHandler)
    logger.info(f"Starting bridge server on port {port}, endpoint {endpoint}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logger.info("Stopping bridge server")
