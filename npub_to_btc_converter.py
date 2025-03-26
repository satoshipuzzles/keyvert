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
    try:
        if not npub or not isinstance(npub, str):
            raise ValueError("Invalid input: npub must be a non-empty string")
            
        # Clean the input
        npub = npub.strip().lower()
        
        # Basic format check
        if not npub.startswith('npub1'):
            raise ValueError("Invalid npub format: must start with 'npub1'")
            
        # Decode bech32
        hrp, data = bech32_decode(npub)
        if hrp is None or data is None:
            raise ValueError("Invalid bech32 encoding")
            
        if hrp != 'npub':
            raise ValueError(f"Invalid prefix: expected 'npub', got '{hrp}'")
            
        # Convert from 5-bit to 8-bit
        pubkey_bytes = convertbits(data, 5, 8, False)
        if pubkey_bytes is None:
            raise ValueError("Invalid data conversion")
            
        # Verify length
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
            
        # Clean input
        pubkey_hex = pubkey_hex.strip().lower()
        
        # Validate hex format
        try:
            int(pubkey_hex, 16)
        except ValueError:
            raise ValueError("Invalid hex format")
            
        # Validate length
        if len(pubkey_hex) != 64:
            raise ValueError(f"Invalid public key length: expected 64 hex chars, got {len(pubkey_hex)}")
            
        # Convert hex to bytes
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        
        # Hash160 (ripemd160(sha256(pubkey)))
        h = hashlib.new('ripemd160')
        h.update(hashlib.sha256(pubkey_bytes).digest())
        pubkey_hash = h.digest()
        
        # Add version byte (0x00 for mainnet)
        version_pubkey_hash = b'\x00' + pubkey_hash
        
        # Double SHA256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(version_pubkey_hash).digest()).digest()[:4]
        
        # Combine and encode
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
            
        # Clean input
        pubkey_hex = pubkey_hex.strip().lower()
        
        # Validate hex format
        try:
            int(pubkey_hex, 16)
        except ValueError:
            raise ValueError("Invalid hex format")
            
        # Validate length
        if len(pubkey_hex) != 64:
            raise ValueError(f"Invalid public key length: expected 64 hex chars, got {len(pubkey_hex)}")
            
        # Convert hex to bytes
        pubkey_bytes = bytes.fromhex(pubkey_hex)
        
        # Hash160 (ripemd160(sha256(pubkey)))
        h = hashlib.new('ripemd160')
        h.update(hashlib.sha256(pubkey_bytes).digest())
        pubkey_hash = h.digest()
        
        # Convert to 5-bit format for bech32
        data = convertbits(pubkey_hash, 8, 5)
        if data is None:
            raise ValueError("Error converting to 5-bit format")
            
        # Encode as bech32 with 'bc' prefix (mainnet)
        # Note: bech32_encode takes only hrp and data, witness version is part of data
        data = [0] + data  # Prepend witness version 0
        address = bech32_encode('bc', data)
        if address is None:
            raise ValueError("Error encoding bech32 address")
            
        return address
    except Exception as e:
        raise ValueError(f"Error converting to SegWit address: {str(e)}")

def nsec_to_hex(nsec):
    """Convert nsec to hex private key."""
    try:
        if not nsec or not isinstance(nsec, str):
            raise ValueError("Invalid input: nsec must be a non-empty string")
            
        # Clean input
        nsec = nsec.strip().lower()
        
        # Basic format check
        if not nsec.startswith('nsec1'):
            raise ValueError("Invalid nsec format: must start with 'nsec1'")
            
        # Decode bech32
        hrp, data = bech32_decode(nsec)
        if hrp is None or data is None:
            raise ValueError("Invalid bech32 encoding")
            
        if hrp != 'nsec':
            raise ValueError(f"Invalid prefix: expected 'nsec', got '{hrp}'")
            
        # Convert from 5-bit to 8-bit
        privkey_bytes = convertbits(data, 5, 8, False)
        if privkey_bytes is None:
            raise ValueError("Invalid data conversion")
            
        # Verify length
        if len(privkey_bytes) != 32:
            raise ValueError(f"Invalid private key length: expected 32 bytes, got {len(privkey_bytes)}")
            
        return bytes(privkey_bytes).hex()
    except Exception as e:
        raise ValueError(f"Error converting nsec: {str(e)}")

def hex_to_wif(privkey_hex):
    """Convert hex private key to WIF format."""
    try:
        if not privkey_hex or not isinstance(privkey_hex, str):
            raise ValueError("Invalid input: privkey_hex must be a non-empty string")
            
        # Clean input
        privkey_hex = privkey_hex.strip().lower()
        
        # Validate hex format
        try:
            int(privkey_hex, 16)
        except ValueError:
            raise ValueError("Invalid hex format")
            
        # Validate length
        if len(privkey_hex) != 64:
            raise ValueError(f"Invalid private key length: expected 64 hex chars, got {len(privkey_hex)}")
            
        # Convert hex to bytes
        privkey_bytes = bytes.fromhex(privkey_hex)
        
        # Add version byte (0x80 for mainnet) and compression byte (0x01)
        version_privkey = b'\x80' + privkey_bytes + b'\x01'
        
        # Double SHA256 for checksum
        checksum = hashlib.sha256(hashlib.sha256(version_privkey).digest()).digest()[:4]
        
        # Combine and encode
        wif_bytes = version_privkey + checksum
        wif = base58.b58encode(wif_bytes).decode('utf-8')
        
        return wif
    except Exception as e:
        raise ValueError(f"Error converting to WIF: {str(e)}")

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
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            })
            
        key_type = data.get('type', 'npub')
        keys = data.get('keys', [])
        
        if not keys:
            return jsonify({
                'success': False,
                'error': 'No keys provided'
            })
        
        if isinstance(keys, str):
            keys = [keys]
        elif not isinstance(keys, list):
            return jsonify({
                'success': False,
                'error': 'Invalid keys format'
            })
        
        results = []
        errors = []
        
        for key in keys:
            try:
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
            except Exception as e:
                errors.append({
                    'key': key,
                    'error': str(e)
                })
        
        if not results and errors:
            return jsonify({
                'success': False,
                'error': 'All conversions failed',
                'errors': errors
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'errors': errors if errors else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
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