"""
Title: Bithub Authentication
Description: Handles RSA key generation and payload decryption for Discourse MCP.
"""

import os
import secrets
import base64
import json
from urllib.parse import urlencode
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

class BithubAuth:
    def __init__(self):
        self.private_key = None
        self.public_key_pem = None

    def generate_key_pair(self):
        # Generates a 2048-bit RSA key pair.
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        public_key = self.private_key.public_key()
        self.public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def save_private_key(self, filename="private_key.pem"):
        # Saves the private key to a file.
        if not self.private_key:
            raise ValueError("Key pair not generated. Call generate_key_pair() first.")

        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        with open(filename, "wb") as f:
            f.write(pem)
        print(f"[+] Private key saved to {filename}")

    def generate_auth_link(self, site_url, app_name, scopes, redirect_url=None):
        # Constructs the authorization URL.
        if not self.public_key_pem:
            self.generate_key_pair()

        client_id = "discourse-mcp"
        nonce = secrets.token_hex(16)

        params = {
            "scopes": scopes,
            "client_id": client_id,
            "nonce": nonce,
            "application_name": app_name,
            "public_key": self.public_key_pem
        }

        if redirect_url:
            params["auth_redirect"] = redirect_url

        base_url = site_url.rstrip("/")
        query_string = urlencode(params)

        return f"{base_url}/user-api-key/new?{query_string}"

    def decrypt_payload(self, encrypted_payload: str) -> str:
        """
        Decrypts the payload received from Discourse.
        Expects a base64 encoded string containing the encrypted JSON.
        """
        if not self.private_key:
            raise ValueError("Private key not available for decryption.")

        # 1. Decode Base64
        try:
            # Remove whitespace just in case
            encrypted_bytes = base64.b64decode(encrypted_payload.strip())
        except Exception as e:
            raise ValueError(f"Invalid base64 payload: {e}")

        # 2. Decrypt using PKCS1v15 padding (standard for Discourse User API)
        try:
            decrypted_bytes = self.private_key.decrypt(
                encrypted_bytes,
                padding.PKCS1v15()
            )
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

if __name__ == "__main__":
    SITE_URL = "https://hub.bitwiki.org"
    APP_NAME = "Agent Zero"
    SCOPES = "read,write,push,notifications,session_info,chat"

    auth = BithubAuth()
    print("Generating RSA Key Pair...")
    auth.generate_key_pair()
    # auth.save_private_key("private_key.pem")

    link = auth.generate_auth_link(SITE_URL, APP_NAME, SCOPES, redirect_url=None)

    print("\n" + "="*60)
    print("AUTHORIZATION URL (Official MCP Style):")
    print(link)
    print("="*60 + "\n")
