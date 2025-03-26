# Keyvert

A secure, offline-capable Nostr key converter that transforms Nostr public keys (npubs) and private keys (nsecs) into Bitcoin addresses and WIF format keys. This tool runs entirely in your browser with no server requirements.

## Features

- Convert Nostr public keys (npubs) to Bitcoin addresses (Legacy and Native SegWit)
- Convert Nostr private keys (nsecs) to Bitcoin WIF format (offline only)
- Generate QR codes for easy scanning
- Batch conversion support
- Completely offline capable
- No server required
- Copy-to-clipboard functionality

## Security Features

- Private key operations work offline only
- Clear security warnings and best practices
- All conversions happen locally in your browser
- No data is ever sent to any server

## Usage

1. Download `keyvert.html` to your computer
2. For public key (npub) conversions:
   - Open `keyvert.html` in your browser
   - Enter npub keys in the input field
   - Click "Convert" to see Bitcoin addresses
   - Use QR codes or copy buttons as needed

3. For private key (nsec) conversions:
   - Disconnect from the internet
   - Open `keyvert.html` in your browser
   - Switch to the "Private Key" tab
   - Enter nsec keys
   - Click "Convert" to see WIF format keys
   - Copy the results
   - Close the browser tab when done

## Security Warning

Never enter private keys (nsecs) on any website while connected to the internet. Always perform private key operations offline. This tool is provided as-is with no warranty. Always verify the results with other tools before using in production.

## License

MIT License 