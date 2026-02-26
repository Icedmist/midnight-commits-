#!/usr/bin/env python3
"""
Secure Communication Utilities
A secure communication toolkit with encryption and authentication.
Features: TLS/SSL connections, certificate validation, secure messaging.
"""

import ssl
import socket
import hashlib
import hmac
import secrets
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
import argparse
import sys
import time


class SecureMessenger:
    """Secure messaging with encryption and authentication."""

    def __init__(self):
        """Initialize secure messenger."""
        self.private_key = None
        self.public_key = None
        self.peer_public_key = None

    def generate_keypair(self):
        """Generate RSA keypair for encryption."""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def get_public_key_pem(self) -> str:
        """Get public key in PEM format."""
        if not self.public_key:
            self.generate_keypair()

        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')

    def set_peer_public_key(self, pem_key: str):
        """Set peer's public key from PEM format."""
        self.peer_public_key = serialization.load_pem_public_key(
            pem_key.encode('utf-8'),
            backend=default_backend()
        )

    def encrypt_message(self, message: str) -> bytes:
        """Encrypt message using peer's public key."""
        if not self.peer_public_key:
            raise ValueError("Peer public key not set")

        message_bytes = message.encode('utf-8')

        encrypted = self.peer_public_key.encrypt(
            message_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted

    def decrypt_message(self, encrypted_message: bytes) -> str:
        """Decrypt message using private key."""
        if not self.private_key:
            raise ValueError("Private key not available")

        decrypted = self.private_key.decrypt(
            encrypted_message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode('utf-8')

    def sign_message(self, message: str) -> bytes:
        """Sign message using private key."""
        if not self.private_key:
            raise ValueError("Private key not available")

        message_bytes = message.encode('utf-8')

        signature = self.private_key.sign(
            message_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def verify_signature(self, message: str, signature: bytes) -> bool:
        """Verify message signature using peer's public key."""
        if not self.peer_public_key:
            raise ValueError("Peer public key not set")

        message_bytes = message.encode('utf-8')

        try:
            self.peer_public_key.verify(
                signature,
                message_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False


class TLSConnection:
    """TLS/SSL connection handler."""

    def __init__(self, host: str, port: int = 443):
        """Initialize TLS connection."""
        self.host = host
        self.port = port
        self.sock = None
        self.ssl_sock = None

    def connect(self, verify_cert: bool = True):
        """Establish TLS connection."""
        # Create socket
        self.sock = socket.create_connection((self.host, self.port))

        # Wrap with SSL
        context = ssl.create_default_context()

        if not verify_cert:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        self.ssl_sock = context.wrap_socket(self.sock, server_hostname=self.host)

    def send_request(self, request: str) -> str:
        """Send HTTP request and get response."""
        if not self.ssl_sock:
            raise ValueError("Not connected")

        self.ssl_sock.send(request.encode('utf-8'))

        response = b""
        while True:
            data = self.ssl_sock.recv(4096)
            if not data:
                break
            response += data

        return response.decode('utf-8', errors='ignore')

    def get_certificate_info(self):
        """Get certificate information."""
        if not self.ssl_sock:
            raise ValueError("Not connected")

        cert = self.ssl_sock.getpeercert()
        if cert:
            return {
                'subject': dict(x[0] for x in cert['subject']),
                'issuer': dict(x[0] for x in cert['issuer']),
                'version': cert['version'],
                'serialNumber': cert['serialNumber'],
                'notBefore': cert['notBefore'],
                'notAfter': cert['notAfter']
            }
        return None

    def close(self):
        """Close the connection."""
        if self.ssl_sock:
            self.ssl_sock.close()
        if self.sock:
            self.sock.close()


class CertificateValidator:
    """Certificate validation utilities."""

    def __init__(self):
        """Initialize certificate validator."""
        self.context = ssl.create_default_context()

    def validate_certificate(self, host: str, port: int = 443) -> dict:
        """Validate SSL certificate for a host."""
        try:
            conn = TLSConnection(host, port)
            conn.connect(verify_cert=True)

            cert_info = conn.get_certificate_info()
            conn.close()

            if cert_info:
                # Check expiration
                not_after = ssl.cert_time_to_seconds(cert_info['notAfter'])
                current_time = time.time()

                return {
                    'valid': True,
                    'expired': current_time > not_after,
                    'days_until_expiry': (not_after - current_time) / (24 * 3600),
                    'subject': cert_info['subject'],
                    'issuer': cert_info['issuer']
                }
            else:
                return {'valid': False, 'error': 'No certificate found'}

        except ssl.SSLError as e:
            return {'valid': False, 'error': str(e)}
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    def check_certificate_chain(self, cert_pem: str) -> bool:
        """Check if certificate chain is valid."""
        try:
            cert = load_pem_x509_certificate(cert_pem.encode('utf-8'), default_backend())

            # Basic validation - check if certificate is not expired
            current_time = time.time()
            not_before = ssl.cert_time_to_seconds(cert.not_valid_before.isoformat())
            not_after = ssl.cert_time_to_seconds(cert.not_valid_after.isoformat())

            return not_before <= current_time <= not_after

        except Exception:
            return False


class SecureChannel:
    """Secure communication channel with HMAC authentication."""

    def __init__(self, key: bytes = None):
        """Initialize secure channel."""
        self.key = key or secrets.token_bytes(32)

    def generate_hmac(self, message: str) -> str:
        """Generate HMAC for message authentication."""
        message_bytes = message.encode('utf-8')
        hmac_obj = hmac.new(self.key, message_bytes, hashlib.sha256)
        return hmac_obj.hexdigest()

    def verify_hmac(self, message: str, received_hmac: str) -> bool:
        """Verify HMAC for message authentication."""
        expected_hmac = self.generate_hmac(message)
        return hmac.compare_digest(expected_hmac, received_hmac)

    def send_secure_message(self, message: str) -> dict:
        """Send message with HMAC authentication."""
        return {
            'message': message,
            'hmac': self.generate_hmac(message),
            'timestamp': time.time()
        }

    def receive_secure_message(self, data: dict, max_age: float = 300) -> tuple:
        """Receive and verify secure message."""
        message = data.get('message')
        received_hmac = data.get('hmac')
        timestamp = data.get('timestamp', 0)

        if not message or not received_hmac:
            return False, "Invalid message format"

        # Check timestamp (prevent replay attacks)
        current_time = time.time()
        if current_time - timestamp > max_age:
            return False, "Message too old"

        # Verify HMAC
        if not self.verify_hmac(message, received_hmac):
            return False, "HMAC verification failed"

        return True, message


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Secure Communication Tool")
    parser.add_argument("action", choices=['check-cert', 'encrypt-msg', 'decrypt-msg', 'sign-msg', 'verify-sig'],
                       help="Action to perform")
    parser.add_argument("--host", help="Host for certificate checking")
    parser.add_argument("--message", help="Message to encrypt/sign")
    parser.add_argument("--encrypted", help="Encrypted message to decrypt")
    parser.add_argument("--signature", help="Signature to verify")
    parser.add_argument("--public-key", help="Public key file (PEM format)")
    parser.add_argument("--private-key", help="Private key file (PEM format)")

    args = parser.parse_args()

    try:
        if args.action == 'check-cert':
            if not args.host:
                print("Error: --host required for certificate checking")
                sys.exit(1)

            validator = CertificateValidator()
            result = validator.validate_certificate(args.host)

            if result['valid']:
                print(f"✓ Certificate valid for {args.host}")
                if result.get('expired'):
                    print("⚠ Certificate is expired")
                else:
                    days = result['days_until_expiry']
                    print(f"Expires in {days:.1f} days")
                print(f"Issuer: {result['issuer'].get('organizationName', 'Unknown')}")
            else:
                print(f"✗ Certificate invalid: {result.get('error', 'Unknown error')}")

        elif args.action in ['encrypt-msg', 'decrypt-msg', 'sign-msg', 'verify-sig']:
            messenger = SecureMessenger()

            if args.action == 'encrypt-msg':
                if not args.message or not args.public_key:
                    print("Error: --message and --public-key required")
                    sys.exit(1)

                with open(args.public_key, 'r') as f:
                    pem_key = f.read()

                messenger.set_peer_public_key(pem_key)
                encrypted = messenger.encrypt_message(args.message)
                print(f"Encrypted: {encrypted.hex()}")

            elif args.action == 'decrypt-msg':
                if not args.encrypted or not args.private_key:
                    print("Error: --encrypted and --private-key required")
                    sys.exit(1)

                # Load private key
                with open(args.private_key, 'rb') as f:
                    private_pem = f.read()

                messenger.private_key = serialization.load_pem_private_key(
                    private_pem, password=None, backend=default_backend()
                )

                encrypted_bytes = bytes.fromhex(args.encrypted)
                decrypted = messenger.decrypt_message(encrypted_bytes)
                print(f"Decrypted: {decrypted}")

            elif args.action == 'sign-msg':
                if not args.message or not args.private_key:
                    print("Error: --message and --private-key required")
                    sys.exit(1)

                # Load private key
                with open(args.private_key, 'rb') as f:
                    private_pem = f.read()

                messenger.private_key = serialization.load_pem_private_key(
                    private_pem, password=None, backend=default_backend()
                )

                signature = messenger.sign_message(args.message)
                print(f"Signature: {signature.hex()}")

            elif args.action == 'verify-sig':
                if not args.message or not args.signature or not args.public_key:
                    print("Error: --message, --signature, and --public-key required")
                    sys.exit(1)

                with open(args.public_key, 'r') as f:
                    pem_key = f.read()

                messenger.set_peer_public_key(pem_key)
                signature_bytes = bytes.fromhex(args.signature)
                valid = messenger.verify_signature(args.message, signature_bytes)
                print(f"Signature verification: {'✓ Valid' if valid else '✗ Invalid'}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()