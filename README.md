# Nostr to Bitcoin Address Converter

A simple web-based tool to convert Nostr public keys (npub) to Bitcoin addresses. This tool generates both Legacy and Native SegWit Bitcoin addresses from a given Nostr public key.

## Features

- Convert Nostr public keys (npub) to:
  - Legacy Bitcoin addresses (1...)
  - Native SegWit addresses (bc1...)
- Generate QR codes for both address types
- Copy addresses to clipboard with one click
- Client-side only - no server required
- Modern, responsive UI

## Usage

1. Open `index.html` in your web browser
2. Enter a valid Nostr public key (starting with "npub1")
3. Click "Convert"
4. View the generated Bitcoin addresses and their QR codes
5. Use the "Copy" buttons to copy addresses to your clipboard

## Local Development

To run this tool locally:

1. Clone this repository:
   ```bash
   git clone https://github.com/satoshipuzzles/keyvert.git
   cd keyvert
   ```

2. Open `index.html` in your web browser
   - You can use Python's built-in HTTP server:
     ```bash
     python -m http.server 8000
     ```
   - Then visit `http://localhost:8000` in your browser

## GitHub Pages Deployment

This tool is designed to work with GitHub Pages. To deploy:

1. Push your changes to the `main` branch
2. Go to your repository settings
3. Under "GitHub Pages", select the `main` branch as the source
4. Your site will be available at `https://[username].github.io/keyvert/`

## Dependencies

- Bootstrap 5.3.2 - UI framework
- QRCode.js 1.5.3 - QR code generation
- Noble-secp256k1 1.2.14 - Cryptographic operations
- CryptoJS 4.2.0 - Cryptographic functions

## Security

This tool performs all conversions client-side in your browser. No private keys or sensitive data are transmitted over the network. However, always verify the generated addresses before use.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
