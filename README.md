# CornyCHAT MCP Server for Cursor

This is a Model Context Protocol (MCP) server implementation for integrating CornyCHAT with Cursor. It provides commands for interacting with CornyCHAT rooms and users.

## Features

- Get list of active rooms
- Get room details
- Create new rooms
- Get user information (including Lightning wallet and Nostr pubkey)
- Get active users across all rooms

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy the `mcp.json` file to your Cursor MCP configuration directory.

## Available Commands

### Get Active Rooms
```python
mcp_cornychat_get_active_rooms()
```

### Get Room Details
```python
mcp_cornychat_get_room_details(room_id="room_name_or_id")
```

### Create Room
```python
mcp_cornychat_create_room(
    name="my_room",
    description="My awesome room",
    logo_uri="https://example.com/logo.png",
    is_stage_only=False,
    is_protected=False,
    owner_pubkey="npub..."  # Optional, will generate if not provided
)
```

### Get User Info
```python
mcp_cornychat_get_user_info(user_id="user_id")
```

### Get Active Users
```python
mcp_cornychat_get_active_users()
```

## API Documentation

The server uses the CornyCHAT API endpoints:

- `/roomlist/` - Get active rooms
- `/rooms/{room_id}` - Get/create room details
- `/users/{user_id}` - Get user information
- `/zapgoal/{emoji}` - Get zap goals

## Contributing

Feel free to submit issues and enhancement requests!

# Nostr npub to Bitcoin Address Converter

A web application that converts Nostr public keys (npubs) to Bitcoin addresses. This tool demonstrates the interoperability between Nostr and Bitcoin networks by leveraging their shared use of the secp256k1 elliptic curve.

## Features

- Convert Nostr npubs to hex public keys
- Generate Bitcoin Legacy (P2PKH) addresses
- Modern, responsive web interface
- Real-time validation and error handling
- Detailed technical information display

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

1. Start the web server:
```bash
python npub_to_btc_converter.py
```

2. Open your web browser and navigate to:
```
http://localhost:5002
```

3. Enter a Nostr npub and click "Convert" to see the corresponding Bitcoin address.

## Technical Details

This converter implements the address derivation process as specified in NIP-BTCADDR:

1. Decodes the bech32-encoded npub to get the public key
2. Performs SHA256 and RIPEMD160 hashing on the public key
3. Adds version byte and checksum
4. Encodes the result in Base58 format

## Security Considerations

- All conversions are performed client-side
- No private keys are ever used or required
- The generated addresses are deterministic
- The tool only generates mainnet addresses

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Nostr Protocol
- Bitcoin Protocol
- Secp256k1 Curve 