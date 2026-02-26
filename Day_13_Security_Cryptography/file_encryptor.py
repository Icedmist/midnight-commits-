#!/usr/bin/env python3
"""
File Encryption/Decryption Tool
A secure file encryption and decryption utility using AES encryption.
Features: AES-256 encryption, key derivation, secure file handling.
"""

import os
import sys
import argparse
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import secrets
import base64
import getpass


class FileEncryptor:
    """AES file encryption/decryption utility."""

    def __init__(self, password: str):
        """Initialize with password for key derivation."""
        self.password = password.encode()
        self.salt = None
        self.key = None

    def _derive_key(self, salt: bytes = None) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        if salt is None:
            salt = secrets.token_bytes(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256-bit key
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )

        self.salt = salt
        self.key = kdf.derive(self.password)
        return self.key

    def encrypt_file(self, input_file: str, output_file: str = None) -> str:
        """Encrypt a file using AES-256."""
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file '{input_file}' not found")

        if output_file is None:
            output_file = input_file + '.encrypted'

        # Derive key
        self._derive_key()

        # Read input file
        with open(input_file, 'rb') as f:
            data = f.read()

        # Generate random IV
        iv = secrets.token_bytes(16)

        # Pad data
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()

        # Encrypt
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # Write encrypted file with salt and IV prepended
        with open(output_file, 'wb') as f:
            f.write(self.salt)  # 16 bytes
            f.write(iv)         # 16 bytes
            f.write(encrypted_data)

        return output_file

    def decrypt_file(self, input_file: str, output_file: str = None) -> str:
        """Decrypt a file encrypted with this tool."""
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file '{input_file}' not found")

        if output_file is None:
            # Remove .encrypted extension if present
            if input_file.endswith('.encrypted'):
                output_file = input_file[:-10]
            else:
                output_file = input_file + '.decrypted'

        # Read encrypted file
        with open(input_file, 'rb') as f:
            encrypted_data = f.read()

        if len(encrypted_data) < 32:  # salt (16) + iv (16)
            raise ValueError("Invalid encrypted file format")

        # Extract salt and IV
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]

        # Derive key using extracted salt
        self._derive_key(salt)

        # Decrypt
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()

        # Write decrypted file
        with open(output_file, 'wb') as f:
            f.write(data)

        return output_file

    def encrypt_text(self, text: str) -> str:
        """Encrypt text and return base64 encoded result."""
        # Derive key
        self._derive_key()

        # Convert text to bytes
        data = text.encode('utf-8')

        # Generate random IV
        iv = secrets.token_bytes(16)

        # Pad data
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()

        # Encrypt
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # Combine salt, IV, and encrypted data
        combined = self.salt + iv + encrypted_data

        # Return base64 encoded
        return base64.b64encode(combined).decode('utf-8')

    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt base64 encoded encrypted text."""
        try:
            # Decode base64
            combined = base64.b64decode(encrypted_text)
        except:
            raise ValueError("Invalid base64 encoded data")

        if len(combined) < 32:
            raise ValueError("Invalid encrypted data format")

        # Extract salt, IV, and ciphertext
        salt = combined[:16]
        iv = combined[16:32]
        ciphertext = combined[32:]

        # Derive key using extracted salt
        self._derive_key(salt)

        # Decrypt
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()

        return data.decode('utf-8')


class SecureFileManager:
    """Secure file operations with integrity checking."""

    def __init__(self, password: str):
        """Initialize secure file manager."""
        self.encryptor = FileEncryptor(password)

    def secure_delete(self, file_path: str, passes: int = 3):
        """Securely delete a file by overwriting it multiple times."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' not found")

        file_size = os.path.getsize(file_path)

        # Overwrite file multiple times
        with open(file_path, 'wb') as f:
            for _ in range(passes):
                f.write(secrets.token_bytes(file_size))
                f.flush()
                os.fsync(f.fileno())

        # Finally delete the file
        os.remove(file_path)

    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        hash_obj = hashes.Hash(hashes.SHA256(), backend=default_backend())

        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                hash_obj.update(chunk)

        return hash_obj.finalize().hex()

    def verify_file_integrity(self, file_path: str, expected_hash: str) -> bool:
        """Verify file integrity by comparing hashes."""
        actual_hash = self.calculate_file_hash(file_path)
        return actual_hash == expected_hash


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="File Encryption Tool")
    parser.add_argument("action", choices=['encrypt', 'decrypt', 'encrypt-text', 'decrypt-text', 'hash', 'verify'],
                       help="Action to perform")
    parser.add_argument("input", help="Input file or text")
    parser.add_argument("--output", help="Output file (optional)")
    parser.add_argument("--password", help="Encryption password (will prompt if not provided)")
    parser.add_argument("--expected-hash", help="Expected hash for verification")

    args = parser.parse_args()

    # Get password securely
    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Enter password: ")

    if not password:
        print("Error: Password is required")
        sys.exit(1)

    try:
        if args.action in ['encrypt', 'decrypt']:
            encryptor = FileEncryptor(password)

            if args.action == 'encrypt':
                output = encryptor.encrypt_file(args.input, args.output)
                print(f"File encrypted successfully: {output}")
            else:
                output = encryptor.decrypt_file(args.input, args.output)
                print(f"File decrypted successfully: {output}")

        elif args.action in ['encrypt-text', 'decrypt-text']:
            encryptor = FileEncryptor(password)

            if args.action == 'encrypt-text':
                encrypted = encryptor.encrypt_text(args.input)
                print(f"Encrypted text: {encrypted}")
            else:
                decrypted = encryptor.decrypt_text(args.input)
                print(f"Decrypted text: {decrypted}")

        elif args.action == 'hash':
            manager = SecureFileManager(password)
            file_hash = manager.calculate_file_hash(args.input)
            print(f"SHA-256 hash: {file_hash}")

        elif args.action == 'verify':
            if not args.expected_hash:
                print("Error: --expected-hash required for verification")
                sys.exit(1)

            manager = SecureFileManager(password)
            valid = manager.verify_file_integrity(args.input, args.expected_hash)
            print(f"File integrity: {'✓ Valid' if valid else '✗ Invalid'}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()