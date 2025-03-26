# KeyVert

A modern, client-side Nostr key converter that transforms Nostr public keys (npub) into Bitcoin addresses. Built with vanilla JavaScript and a sleek dark theme.

## Features

- Convert Nostr public keys (npub) to Bitcoin addresses
- Generate both Legacy and SegWit addresses
- Automatic QR code generation
- Copy-to-clipboard functionality
- Modern dark theme interface
- Fully client-side - no server required
- Mobile responsive design

## Usage

1. Open `index.html` in your web browser
2. Enter a Nostr public key (starting with `npub1`)
3. Click "Convert" or press Enter
4. View the generated Legacy and SegWit addresses
5. Use the QR codes or copy buttons as needed

## Technical Details

KeyVert implements:
- Bech32 encoding/decoding
- Bitcoin address generation (Legacy P2PKH and SegWit P2WPKH)
- SHA256 and RIPEMD160 hashing
- Base58Check encoding
- QR code generation

## Dependencies

- [CryptoJS](https://github.com/brix/crypto-js) - For cryptographic functions
- [QRCode.js](https://github.com/davidshimjs/qrcodejs) - For QR code generation

## Development

This is a single-file application. To modify:
1. Clone the repository
2. Edit `index.html`
3. Test in your browser

## License

MIT License

## Author

Created by SatoshiPuzzles 