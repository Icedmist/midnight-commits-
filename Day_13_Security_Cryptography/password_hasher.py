#!/usr/bin/env python3
"""
Password Hashing Utilities
A comprehensive password hashing and verification system.
Features: Multiple hashing algorithms, salt generation, and secure password policies.
"""

import hashlib
import bcrypt
import argon2
import secrets
import string
import re
from typing import Optional, Dict, Any
import argparse
import sys


class PasswordHasher:
    """A comprehensive password hashing utility."""

    def __init__(self, algorithm: str = 'bcrypt'):
        """Initialize the password hasher with specified algorithm."""
        self.algorithm = algorithm.lower()
        self._validate_algorithm()

    def _validate_algorithm(self):
        """Validate the chosen hashing algorithm."""
        supported = ['bcrypt', 'argon2', 'pbkdf2', 'scrypt']
        if self.algorithm not in supported:
            raise ValueError(f"Unsupported algorithm. Choose from: {supported}")

    def hash_password(self, password: str) -> str:
        """Hash a password using the specified algorithm."""
        if self.algorithm == 'bcrypt':
            return self._hash_bcrypt(password)
        elif self.algorithm == 'argon2':
            return self._hash_argon2(password)
        elif self.algorithm == 'pbkdf2':
            return self._hash_pbkdf2(password)
        elif self.algorithm == 'scrypt':
            return self._hash_scrypt(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        if self.algorithm == 'bcrypt':
            return self._verify_bcrypt(password, hashed)
        elif self.algorithm == 'argon2':
            return self._verify_argon2(password, hashed)
        elif self.algorithm == 'pbkdf2':
            return self._verify_pbkdf2(password, hashed)
        elif self.algorithm == 'scrypt':
            return self._verify_scrypt(password, hashed)

    def _hash_bcrypt(self, password: str) -> str:
        """Hash password using bcrypt."""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    def _verify_bcrypt(self, password: str, hashed: str) -> bool:
        """Verify password using bcrypt."""
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    def _hash_argon2(self, password: str) -> str:
        """Hash password using Argon2."""
        password_bytes = password.encode('utf-8')
        hash_obj = argon2.hash_password(password_bytes)
        return hash_obj.decode('utf-8')

    def _verify_argon2(self, password: str, hashed: str) -> bool:
        """Verify password using Argon2."""
        try:
            password_bytes = password.encode('utf-8')
            argon2.verify_password(password_bytes, hashed.encode('utf-8'))
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False

    def _hash_pbkdf2(self, password: str) -> str:
        """Hash password using PBKDF2."""
        password_bytes = password.encode('utf-8')
        salt = secrets.token_bytes(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000)
        # Store salt with hash
        return f"{salt.hex()}:{hash_obj.hex()}"

    def _verify_pbkdf2(self, password: str, hashed: str) -> bool:
        """Verify password using PBKDF2."""
        try:
            salt_hex, hash_hex = hashed.split(':')
            salt = bytes.fromhex(salt_hex)
            stored_hash = bytes.fromhex(hash_hex)
            password_bytes = password.encode('utf-8')
            computed_hash = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, 100000)
            return computed_hash == stored_hash
        except ValueError:
            return False

    def _hash_scrypt(self, password: str) -> str:
        """Hash password using scrypt."""
        password_bytes = password.encode('utf-8')
        salt = secrets.token_bytes(16)
        hash_obj = hashlib.scrypt(password_bytes, salt=salt, n=16384, r=8, p=1)
        return f"{salt.hex()}:{hash_obj.hex()}"

    def _verify_scrypt(self, password: str, hashed: str) -> bool:
        """Verify password using scrypt."""
        try:
            salt_hex, hash_hex = hashed.split(':')
            salt = bytes.fromhex(salt_hex)
            stored_hash = bytes.fromhex(hash_hex)
            password_bytes = password.encode('utf-8')
            computed_hash = hashlib.scrypt(password_bytes, salt=salt, n=16384, r=8, p=1)
            return computed_hash == stored_hash
        except ValueError:
            return False


class PasswordPolicy:
    """Password policy enforcement and validation."""

    def __init__(self, min_length: int = 8, require_uppercase: bool = True,
                 require_lowercase: bool = True, require_digits: bool = True,
                 require_special: bool = True):
        """Initialize password policy."""
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special

    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password against policy."""
        issues = []

        if len(password) < self.min_length:
            issues.append(f"Password must be at least {self.min_length} characters long")

        if self.require_uppercase and not re.search(r'[A-Z]', password):
            issues.append("Password must contain at least one uppercase letter")

        if self.require_lowercase and not re.search(r'[a-z]', password):
            issues.append("Password must contain at least one lowercase letter")

        if self.require_digits and not re.search(r'\d', password):
            issues.append("Password must contain at least one digit")

        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must contain at least one special character")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'strength': self._calculate_strength(password)
        }

    def _calculate_strength(self, password: str) -> str:
        """Calculate password strength."""
        score = 0

        if len(password) >= self.min_length:
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        if len(password) >= 12:
            score += 1

        if score <= 2:
            return "Weak"
        elif score <= 4:
            return "Medium"
        else:
            return "Strong"


class PasswordGenerator:
    """Secure password generator."""

    def __init__(self):
        """Initialize password generator."""
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.special = "!@#$%^&*(),.?\":{}|<>"

    def generate_password(self, length: int = 12, use_uppercase: bool = True,
                         use_digits: bool = True, use_special: bool = True) -> str:
        """Generate a secure random password."""
        if length < 4:
            raise ValueError("Password length must be at least 4")

        # Ensure at least one character from each required category
        password = [secrets.choice(self.lowercase)]

        if use_uppercase:
            password.append(secrets.choice(self.uppercase))
        if use_digits:
            password.append(secrets.choice(self.digits))
        if use_special:
            password.append(secrets.choice(self.special))

        # Fill the rest randomly
        all_chars = self.lowercase
        if use_uppercase:
            all_chars += self.uppercase
        if use_digits:
            all_chars += self.digits
        if use_special:
            all_chars += self.special

        while len(password) < length:
            password.append(secrets.choice(all_chars))

        # Shuffle the password
        secrets.SystemRandom().shuffle(password)

        return ''.join(password)


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Password Security Tool")
    parser.add_argument("action", choices=['hash', 'verify', 'generate', 'validate'],
                       help="Action to perform")
    parser.add_argument("--password", help="Password to hash or verify")
    parser.add_argument("--hash", help="Hash to verify against")
    parser.add_argument("--algorithm", choices=['bcrypt', 'argon2', 'pbkdf2', 'scrypt'],
                       default='bcrypt', help="Hashing algorithm (default: bcrypt)")
    parser.add_argument("--length", type=int, default=12, help="Generated password length (default: 12)")
    parser.add_argument("--no-uppercase", action="store_true", help="Don't use uppercase in generated password")
    parser.add_argument("--no-digits", action="store_true", help="Don't use digits in generated password")
    parser.add_argument("--no-special", action="store_true", help="Don't use special chars in generated password")

    args = parser.parse_args()

    try:
        if args.action == 'hash':
            if not args.password:
                print("Error: --password required for hashing")
                sys.exit(1)

            hasher = PasswordHasher(args.algorithm)
            hashed = hasher.hash_password(args.password)
            print(f"Hashed password: {hashed}")

        elif args.action == 'verify':
            if not args.password or not args.hash:
                print("Error: --password and --hash required for verification")
                sys.exit(1)

            hasher = PasswordHasher(args.algorithm)
            valid = hasher.verify_password(args.password, args.hash)
            print(f"Password verification: {'✓ Valid' if valid else '✗ Invalid'}")

        elif args.action == 'generate':
            generator = PasswordGenerator()
            password = generator.generate_password(
                length=args.length,
                use_uppercase=not args.no_uppercase,
                use_digits=not args.no_digits,
                use_special=not args.no_special
            )
            print(f"Generated password: {password}")

        elif args.action == 'validate':
            if not args.password:
                print("Error: --password required for validation")
                sys.exit(1)

            policy = PasswordPolicy()
            result = policy.validate_password(args.password)
            print(f"Password strength: {result['strength']}")
            if result['valid']:
                print("✓ Password meets all requirements")
            else:
                print("✗ Password validation failed:")
                for issue in result['issues']:
                    print(f"  - {issue}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()