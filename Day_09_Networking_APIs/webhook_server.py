"""
Webhook Listener Server
Receive and process webhooks with signature validation
"""

from flask import Flask, request, jsonify
from typing import Dict, Callable, Optional
import hmac
import hashlib
import json
import logging
from datetime import datetime
from threading import Thread
import queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebhookServer:
    """Flask-based webhook server"""

    def __init__(self, secret: str = None, port: int = 5000):
        """Initialize webhook server"""
        self.app = Flask(__name__)
        self.secret = secret
        self.port = port
        self.handlers: Dict[str, Callable] = {}
        self.events_queue = queue.Queue()
        self.setup_routes()

    def setup_routes(self) -> None:
        """Setup Flask routes"""
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({"status": "ok"}), 200

        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            # Verify signature
            if not self._verify_signature(request):
                logger.warning("❌ Invalid signature")
                return jsonify({"error": "Unauthorized"}), 401

            data = request.get_json()
            event_type = data.get('type', 'unknown')

            logger.info(f"📨 Webhook received: {event_type}")

            # Queue event for processing
            self.events_queue.put({
                'type': event_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })

            # Call handler if registered
            if event_type in self.handlers:
                try:
                    self.handlers[event_type](data)
                except Exception as e:
                    logger.error(f"❌ Handler error: {e}")

            return jsonify({"status": "received"}), 200

    def _verify_signature(self, req: request) -> bool:
        """Verify webhook signature"""
        if not self.secret:
            return True

        signature = req.headers.get('X-Signature')
        if not signature:
            return False

        body = req.get_data()
        expected = hmac.new(
            self.secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected)

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Register event handler"""
        self.handlers[event_type] = handler
        logger.info(f"✅ Handler registered: {event_type}")

    def get_events(self) -> list:
        """Get queued events"""
        events = []
        while not self.events_queue.empty():
            events.append(self.events_queue.get())
        return events

    def run(self, debug: bool = False) -> None:
        """Run server"""
        logger.info(f"🚀 Webhook server running on port {self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=debug)

    def run_async(self, debug: bool = False) -> Thread:
        """Run server in background thread"""
        thread = Thread(target=self.run, args=(debug,), daemon=True)
        thread.start()
        logger.info(f"🧵 Server thread started")
        return thread


class WebhookClient:
    """Send webhooks to server"""

    def __init__(self, webhook_url: str, secret: str = None):
        """Initialize webhook client"""
        self.webhook_url = webhook_url
        self.secret = secret

    def send_event(self, event_type: str, data: Dict) -> bool:
        """Send webhook event"""
        import requests

        payload = {
            'type': event_type,
            **data
        }

        headers = {
            'Content-Type': 'application/json'
        }

        # Sign payload
        if self.secret:
            body = json.dumps(payload).encode()
            signature = hmac.new(
                self.secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            headers['X-Signature'] = signature

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=headers,
                timeout=5
            )
            logger.info(f"✅ Webhook sent: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Webhook failed: {e}")
            return False


def demo_webhook():
    """Demo webhook server"""
    # Create server
    server = WebhookServer(secret="my-secret-key", port=5555)

    # Register handlers
    def handle_payment(data):
        print(f"💰 Payment processed: {data}")

    def handle_user_signup(data):
        print(f"👤 New user: {data}")

    server.register_handler('payment', handle_payment)
    server.register_handler('user_signup', handle_user_signup)

    # Run server
    print("\n🔔 Webhook Server\n")
    print("Listening on http://localhost:5555/webhook")
    # server.run()


if __name__ == "__main__":
    print("🔔 Webhook Listener Server\n")
    print("Features:")
    print("✓ Webhook reception")
    print("✓ Signature verification")
    print("✓ Event queuing")
    print("✓ Custom handlers")
    print("\nRequires: pip install flask requests")
