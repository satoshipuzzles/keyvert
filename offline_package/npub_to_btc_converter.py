from flask import Flask, render_template, request, jsonify, send_file
import hashlib
import base58
from bech32 import bech32_decode, convertbits, bech32_encode
import qrcode
from io import BytesIO
import os
import warnings

app = Flask(__name__)

def npub_to_hex(npub):
    """Convert npub to hex public key."""
    hrp, data = bech32_decode(npub)
    if hrp != 'npub':
        raise ValueError("Invalid npub format")
    pubkey_bytes = convertbits(data, 5, 8, False)
    return bytes(pubkey_bytes).hex()

def hex_to_legacy_address(pubkey_hex):
    """Convert hex public key to Bitcoin legacy address."""
    pubkey_bytes = bytes.fromhex(pubkey_hex)
    sha256_hash = hashlib.sha256(pubkey_bytes).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    version_ripemd160_hash = b'\x00' + ripemd160_hash
    double_sha256 = hashlib.sha256(hashlib.sha256(version_ripemd160_hash).digest()).digest()
    checksum = double_sha256[:4]
    binary_addr = version_ripemd160_hash + checksum
    return base58.b58encode(binary_addr).decode()

def hex_to_segwit_address(pubkey_hex):
    """Convert hex public key to Native SegWit address."""
    pubkey_bytes = bytes.fromhex(pubkey_hex)
    sha256_hash = hashlib.sha256(pubkey_bytes).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    words = convertbits(ripemd160_hash, 8, 5)
    return bech32_encode('bc', words)

def nsec_to_hex(nsec):
    """Convert nsec to hex private key."""
    hrp, data = bech32_decode(nsec)
    if hrp != 'nsec':
        raise ValueError("Invalid nsec format")
    privkey_bytes = convertbits(data, 5, 8, False)
    return bytes(privkey_bytes).hex()

def hex_to_wif(privkey_hex):
    """Convert hex private key to WIF format."""
    # Add version byte (0x80 for mainnet)
    extended_key = b'\x80' + bytes.fromhex(privkey_hex)
    
    # Add compression byte
    extended_key += b'\x01'
    
    # Double SHA256 for checksum
    double_sha256 = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()
    checksum = double_sha256[:4]
    
    # Combine everything and encode in base58
    final_key = extended_key + checksum
    return base58.b58encode(final_key).decode()

def generate_qr(data):
    """Generate QR code for the given data."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.json
        key_type = data.get('type', 'npub')
        keys = data.get('keys', [])
        
        if isinstance(keys, str):
            keys = [keys]
        
        results = []
        for key in keys:
            if key_type == 'npub':
                hex_pubkey = npub_to_hex(key)
                legacy_address = hex_to_legacy_address(hex_pubkey)
                segwit_address = hex_to_segwit_address(hex_pubkey)
                
                results.append({
                    'npub': key,
                    'hex_pubkey': hex_pubkey,
                    'legacy_address': legacy_address,
                    'segwit_address': segwit_address
                })
            elif key_type == 'nsec':
                hex_privkey = nsec_to_hex(key)
                wif_key = hex_to_wif(hex_privkey)
                
                results.append({
                    'nsec': key,
                    'hex_privkey': hex_privkey,
                    'wif': wif_key
                })
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/qr/<address>')
def get_qr(address):
    try:
        img_io = generate_qr(address)
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, port=5002) 