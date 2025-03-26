from flask import Flask, render_template, jsonify
import requests
import hashlib
import base58
import bech32
import logging
from bip_utils import Bech32

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def get_active_users():
    """Fetch active users from CornyChat API"""
    try:
        response = requests.get('http://127.0.0.1:5001/users/active')
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to fetch users: {response.status_code}")
            return []
    except Exception as e:
        logging.error(f"Error fetching users: {e}")
        return []

def npub_to_bitcoin_addresses(npub):
    """Convert a Nostr public key to both Legacy and Native SegWit Bitcoin addresses"""
    try:
        # Decode npub
        decoded = Bech32.decode("npub", npub)
        if not decoded:
            return None, None
        
        pubkey_bytes = bytes.fromhex(decoded[1].hex())
        
        # Legacy address (P2PKH)
        sha256_hash = hashlib.sha256(pubkey_bytes).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        version_ripemd160_hash = b'\x00' + ripemd160_hash
        double_sha256 = hashlib.sha256(hashlib.sha256(version_ripemd160_hash).digest()).digest()
        checksum = double_sha256[:4]
        binary_addr = version_ripemd160_hash + checksum
        legacy_address = base58.b58encode(binary_addr).decode()
        
        # Native SegWit address (P2WPKH)
        wpkh = hashlib.new('ripemd160', hashlib.sha256(pubkey_bytes).digest()).digest()
        bech32_address = bech32.encode('bc', 0, wpkh)
        
        return legacy_address, bech32_address
    except Exception as e:
        logging.error(f"Error converting npub: {e}")
        return None, None

@app.route('/')
def index():
    users = get_active_users()
    user_addresses = []
    
    for user in users:
        legacy_addr, bech32_addr = npub_to_bitcoin_addresses(user['npub'])
        user_addresses.append({
            'username': user['username'],
            'npub': user['npub'],
            'legacy_address': legacy_addr,
            'bech32_address': bech32_addr
        })
    
    return render_template('cornybtc.html', users=user_addresses)

@app.route('/api/users')
def api_users():
    users = get_active_users()
    user_addresses = []
    
    for user in users:
        legacy_addr, bech32_addr = npub_to_bitcoin_addresses(user['npub'])
        user_addresses.append({
            'username': user['username'],
            'npub': user['npub'],
            'legacy_address': legacy_addr,
            'bech32_address': bech32_addr
        })
    
    return jsonify(user_addresses)

if __name__ == '__main__':
    app.run(port=5003, debug=True) 