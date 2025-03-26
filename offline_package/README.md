# Nostr Key Converter - Offline Package

This is a standalone version of the Nostr Key Converter that can be run offline for enhanced security, especially when dealing with private keys.

## Security Considerations

1. **Private Keys**: Never enter private keys (nsec) on any online website. Always use this offline version for private key operations.
2. **Air-gapped Computer**: For maximum security, use an air-gapped computer that has never been and will never be connected to the internet.
3. **Clean Environment**: Use a fresh OS installation or a live USB boot for sensitive operations.

## Installation Instructions

1. Install Python 3.7+ if not already installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Open a terminal in this directory
2. Run the converter:
   ```bash
   python npub_to_btc_converter.py
   ```
3. Open your browser to `http://localhost:5002`

## Features

- Convert Nostr public keys (npubs) to:
  - Legacy Bitcoin addresses (P2PKH)
  - Native SegWit addresses (P2WPKH)
  - Generate QR codes for addresses
- Convert Nostr private keys (nsecs) to:
  - WIF format private keys
  - Hex format private keys
- Batch conversion support
- Copy-to-clipboard functionality
- All operations performed locally

## Example Keys for Testing

Public key (npub):
```
npub12r0yjt8723ey2r035qtklhmdj90f0j6an7xnan8005jl7z5gw80qat9qrx
```

Expected results:
- Legacy address: `18smGGTPH9GNuNVbRAoCqm5BiU5yX86h1D`
- Native SegWit: `bc12e32pttcj9v5hj2w2m8t88ppwzsjhwwvmmvez6`

## Verifying the Installation

1. Test the converter with the example public key above
2. Verify the addresses match the expected results
3. Ensure QR code generation works
4. Test the copy-to-clipboard functionality

## Troubleshooting

1. Port in use error:
   - Change the port in `npub_to_btc_converter.py` from 5002 to another number
   - Restart the application

2. Missing dependencies:
   - Ensure all requirements are installed: `pip install -r requirements.txt`
   - For QR code issues: `pip install "qrcode[pil]"`

## Support

This is an offline tool. For updates or issues, visit the project repository when online. 