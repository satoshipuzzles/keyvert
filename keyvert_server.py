import os
import json
import secrets
import requests
import hashlib
import base58
from bech32 import bech32_decode, convertbits, bech32_encode
import qrcode
from io import BytesIO
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import sys
import asyncio
from flask import Flask, jsonify, request, render_template, send_file
from flask_cors import CORS
import logging
import warnings

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# CornyCHAT Configuration and API Class
@dataclass
class CornyChatConfig:
    base_url: str = "https://cornychat.com/_/pantry/api/v1"
    auth_token: Optional[str] = None
    pubkey: Optional[str] = None
    signature: Optional[str] = None

class CornyChatAPI:
    def __init__(self, config: Optional[CornyChatConfig] = None):
        self.config = config or CornyChatConfig()
        self.base_url = self.config.base_url

    def _get_headers(self) -> dict:
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.config and self.config.pubkey and self.config.signature:
            headers.update({
                "X-Auth-Pubkey": self.config.pubkey,
                "X-Auth-Signature": self.config.signature
            })
        return headers

    def authenticate(self, pubkey: str, signature: str) -> Dict:
        """Authenticate a user with their public key and signature"""
        try:
            if not pubkey or not isinstance(pubkey, str):
                raise ValueError("Invalid pubkey format")
            if not signature or not isinstance(signature, str):
                raise ValueError("Invalid signature format")

            pubkey = pubkey.strip()
            signature = signature.strip()

            if pubkey.startswith("gen_"):
                if signature[:16] == pubkey[4:]:
                    self.config.pubkey = pubkey
                    self.config.signature = signature
                    return {"success": True, "message": "Authenticated successfully"}
                else:
                    raise ValueError("Invalid signature for generated keypair")

            response = requests.post(
                f"{self.config.base_url}/auth",
                headers={"Content-Type": "application/json"},
                json={"pubkey": pubkey, "signature": signature}
            )
            response.raise_for_status()
            
            auth_data = response.json()
            if auth_data.get("success"):
                self.config.pubkey = pubkey
                self.config.signature = signature
                return auth_data
            else:
                raise ValueError(auth_data.get("error", "Authentication failed"))
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Authentication failed: {str(e)}")
            if e.response.status_code == 401:
                raise ValueError("Invalid credentials")
            elif e.response.status_code == 429:
                raise ValueError("Too many authentication attempts")
            else:
                raise ValueError(f"Authentication failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            raise ValueError(f"Authentication error: {str(e)}")

    def get_active_rooms(self) -> List[Dict]:
        """Fetch all active rooms and their users"""
        logger.debug("Fetching active rooms")
        response = requests.get(
            f"{self.config.base_url}/roomlist/",
            headers=self._get_headers()
        )
        response.raise_for_status()
        rooms = response.json()
        logger.debug(f"Successfully fetched {len(rooms)} rooms")
        return rooms

    def get_room_details(self, room_id: str) -> Dict:
        """Get room details including active users"""
        rooms = self.get_active_rooms()
        room = next((r for r in rooms if r["roomId"] == room_id or r["name"] == room_id), None)
        
        if room:
            return room
            
        response = requests.get(
            f"{self.config.base_url}/rooms/{room_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def get_user_info(self, user_id: str) -> Dict:
        """Get user information"""
        response = requests.get(
            f"{self.config.base_url}/users/{user_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def get_total_active_users(self) -> int:
        """Get total number of active users across all rooms"""
        rooms = self.get_active_rooms()
        return sum(room.get("userCount", 0) for room in rooms)

# Key Conversion Functions
def npub_to_hex(npub):
    """Convert npub to hex public key."""
    try:
        if not npub or not isinstance(npub, str):
            raise ValueError("Invalid input: npub must be a non-empty string")
            
        npub = npub.strip().lower()
        
        if not npub.startswith('npub1'):
            raise ValueError("Invalid npub format: must start with 'npub1'")
            
        hrp, data = bech32_decode(npub)
        if hrp is None or data is None:
            raise ValueError("Invalid bech32 encoding")
            
        if hrp != 'npub':
            raise ValueError(f"Invalid prefix: expected 'npub', got '{hrp}'")
            
        pubkey_bytes = convertbits(data, 5, 8, False)
        if pubkey_bytes is None:
            raise ValueError("Invalid data conversion")
            
        if len(pubkey_bytes) != 32:
            raise ValueError(f"Invalid public key length: expected 32 bytes, got {len(pubkey_bytes)}")
            
        return bytes(pubkey_bytes).hex()
    except Exception as e:
        raise ValueError(f"Error converting npub: {str(e)}")

def hex_to_legacy_address(pubkey_hex):
    """Convert hex public key to legacy Bitcoin address."""
    try:
        if not pubkey_hex or not isinstance(pubkey_hex, str):
            raise ValueError("Invalid input: pubkey_hex must be a non-empty string")
            
        pubkey_hex = pubkey_hex.strip().lower()
        
        try:
            int(pubkey_hex, 16)
        except ValueError:
            raise ValueError("Invalid hex format")
            
        if len(pubkey_hex) != 64:
            raise ValueError(f"Invalid public key length: expected 64 hex chars, got {len(pubkey_hex)}")
            
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        
        h = hashlib.new('ripemd160')
        h.update(hashlib.sha256(pubkey_bytes).digest())
        pubkey_hash = h.digest()
        
        version_pubkey_hash = b'\x00' + pubkey_hash
        
        checksum = hashlib.sha256(hashlib.sha256(version_pubkey_hash).digest()).digest()[:4]
        
        address_bytes = version_pubkey_hash + checksum
        address = base58.b58encode(address_bytes).decode('utf-8')
        
        return address
    except Exception as e:
        raise ValueError(f"Error converting to legacy address: {str(e)}")

def hex_to_segwit_address(pubkey_hex):
    """Convert hex public key to native SegWit (bech32) address."""
    try:
        if not pubkey_hex or not isinstance(pubkey_hex, str):
            raise ValueError("Invalid input: pubkey_hex must be a non-empty string")
            
        pubkey_hex = pubkey_hex.strip().lower()
        
        try:
            int(pubkey_hex, 16)
        except ValueError:
            raise ValueError("Invalid hex format")
            
        if len(pubkey_hex) != 64:
            raise ValueError(f"Invalid public key length: expected 64 hex chars, got {len(pubkey_hex)}")
            
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        
        h = hashlib.new('ripemd160')
        h.update(hashlib.sha256(pubkey_bytes).digest())
        pubkey_hash = h.digest()
        
        data = convertbits(pubkey_hash, 8, 5)
        if data is None:
            raise ValueError("Error converting to 5-bit format")
            
        data = [0] + data  # Prepend witness version 0
        address = bech32_encode('bc', data)
        if address is None:
            raise ValueError("Error encoding bech32 address")
            
        return address
    except Exception as e:
        raise ValueError(f"Error converting to SegWit address: {str(e)}")

def generate_qr(data):
    """Generate QR code for given data."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

def get_address_balance(address: str) -> Dict:
    """Get balance for a Bitcoin address using Blockstream API."""
    try:
        response = requests.get(f"https://blockstream.info/api/address/{address}")
        response.raise_for_status()
        data = response.json()
        
        # Convert satoshis to BTC
        balance_btc = data.get("chain_stats", {}).get("funded_txo_sum", 0) / 100000000
        unspent_btc = data.get("chain_stats", {}).get("spent_txo_sum", 0) / 100000000
        
        return {
            "balance": balance_btc,
            "unspent": unspent_btc,
            "tx_count": data.get("chain_stats", {}).get("tx_count", 0)
        }
    except Exception as e:
        logger.error(f"Error fetching balance: {str(e)}")
        return {"error": "Failed to fetch balance"}

# Initialize CornyCHAT API
corny_api = CornyChatAPI()

# Routes for Key Conversion
@app.route('/')
def index():
    """Render the main page with both key conversion and CornyCHAT features."""
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    """Convert Nostr public key to Bitcoin addresses."""
    try:
        data = request.get_json()
        if not data or 'npub' not in data:
            return jsonify({"error": "Missing npub in request"}), 400

        npub = data['npub']
        hex_pubkey = npub_to_hex(npub)
        legacy_address = hex_to_legacy_address(hex_pubkey)
        segwit_address = hex_to_segwit_address(hex_pubkey)

        return jsonify({
            "npub": npub,
            "hex_pubkey": hex_pubkey,
            "legacy_address": legacy_address,
            "segwit_address": segwit_address
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/qr/<address>')
def get_qr(address):
    """Generate QR code for a Bitcoin address."""
    try:
        img_io = generate_qr(address)
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        logger.error(f"QR generation error: {str(e)}")
        return jsonify({"error": "Failed to generate QR code"}), 500

@app.route('/balance/<address>')
def check_balance(address):
    """Get balance for a Bitcoin address."""
    try:
        balance_info = get_address_balance(address)
        return jsonify(balance_info)
    except Exception as e:
        logger.error(f"Balance check error: {str(e)}")
        return jsonify({"error": "Failed to check balance"}), 500

# Routes for CornyCHAT API
@app.route("/roomlist/")
def get_rooms():
    """Get list of active rooms."""
    try:
        rooms = corny_api.get_active_rooms()
        return jsonify(rooms)
    except Exception as e:
        logger.error(f"Error fetching rooms: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/rooms/<room_id>")
def get_room(room_id):
    """Get details for a specific room."""
    try:
        room = corny_api.get_room_details(room_id)
        return jsonify(room)
    except Exception as e:
        logger.error(f"Error fetching room details: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/users/active")
def get_active_users():
    """Get total number of active users."""
    try:
        logger.debug("Fetching active users")
        total_users = corny_api.get_total_active_users()
        logger.debug(f"Found {total_users} active users")
        return jsonify({"total_users": total_users})
    except Exception as e:
        logger.error(f"Error fetching active users: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/auth", methods=["POST"])
def authenticate():
    """Authenticate a user."""
    try:
        data = request.get_json()
        if not data or "pubkey" not in data or "signature" not in data:
            return jsonify({"error": "Missing pubkey or signature"}), 400

        result = corny_api.authenticate(data["pubkey"], data["signature"])
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True) 