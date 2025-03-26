# Keyvert - Nostr Key Converter & CornyCHAT Integration

A secure, offline-first tool for converting Nostr keys to Bitcoin format, with additional CornyCHAT integration capabilities. Convert your npubs to Bitcoin addresses, nsecs to WIF format private keys, and interact with CornyCHAT rooms and users.

## Key Converter Features

- Convert Nostr public keys (npubs) to:
  - Legacy Bitcoin addresses (P2PKH)
  - Native SegWit addresses (P2WPKH)
- Convert Nostr private keys (nsecs) to Bitcoin WIF format
- Batch conversion support (multiple keys at once)
- QR code generation for addresses
- Copy-to-clipboard functionality
- Completely offline operation for private keys
- No server-side processing for key conversions

## CornyCHAT Integration Features

- Get list of active rooms
- Get room details
- Create new rooms
- Get user information (including Lightning wallet and Nostr pubkey)
- Get active users across all rooms

## Security Features

- Enforced offline mode for private key operations
- Clear security warnings and instructions
- No data transmission for key conversions - works entirely in your browser
- Open source code for transparency

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Key Converter

1. Start the web server:
```bash
python npub_to_btc_converter.py
```

2. Open your web browser and navigate to:
```
http://localhost:5002
```

3. Enter Nostr keys and click "Convert" to see the corresponding Bitcoin addresses.

### CornyCHAT Integration

Available commands through the MCP server:

```python
# Get active rooms
mcp_cornychat_get_active_rooms()

# Get room details
mcp_cornychat_get_room_details(room_id="room_name_or_id")

# Create room
mcp_cornychat_create_room(
    name="my_room",
    description="My awesome room",
    logo_uri="https://example.com/logo.png",
    is_stage_only=False,
    is_protected=False,
    owner_pubkey="npub..."  # Optional
)

# Get user info
mcp_cornychat_get_user_info(user_id="user_id")

# Get active users
mcp_cornychat_get_active_users()
```

## Technical Details

The key converter implements the address derivation process as specified in NIP-BTCADDR:

1. Decodes the bech32-encoded npub to get the public key
2. Performs SHA256 and RIPEMD160 hashing on the public key
3. Adds version byte and checksum
4. Encodes the result in Base58 format for legacy addresses or Bech32 for SegWit

## Security Notice

⚠️ **NEVER enter private keys (nsecs) on any website while connected to the internet. Always perform private key operations offline.**

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
