# Keyvert - Nostr Key Converter

A secure, offline-first tool for converting Nostr keys to Bitcoin format. Convert your npubs to Bitcoin addresses and nsecs to WIF format private keys.

## Features

- Convert Nostr public keys (npubs) to:
  - Legacy Bitcoin addresses (P2PKH)
  - Native SegWit addresses (P2WPKH)
- Convert Nostr private keys (nsecs) to Bitcoin WIF format
- Batch conversion support (multiple keys at once)
- QR code generation for addresses
- Copy-to-clipboard functionality
- Completely offline operation for private keys
- No server-side processing - all conversions happen in your browser

## Security Features

- Enforced offline mode for private key operations
- Clear security warnings and instructions
- No data transmission - works entirely in your browser
- Open source code for transparency

## Usage

1. For public key (npub) conversion:
   - Visit the tool in your browser
   - Enter one or more npubs (one per line)
   - Click "Convert" to see Bitcoin addresses and QR codes

2. For private key (nsec) conversion:
   - Save the HTML file to your computer
   - Disconnect from the internet
   - Open the saved file in your browser
   - Enter your nsec(s)
   - Click "Convert" to see WIF format keys

## Development

This is a pure HTML/JavaScript application with no build process required. It uses:

- TailwindCSS for styling
- Noble Secp256k1 for cryptographic operations
- QRCode.js for QR code generation
- Bech32 for address encoding
- Base58 for WIF encoding

## License

MIT License - See LICENSE file for details.

## Security Notice

⚠️ **NEVER enter private keys (nsecs) on any website while connected to the internet. Always perform private key operations offline.**

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 