NIP-BTCADDR
===========

Bitcoin Address Derivation from Nostr Public Keys
----------------------------------------------

`draft` `optional` `author:kennyalves`

This NIP defines a standard method for deriving Bitcoin addresses from Nostr public keys, enabling seamless integration between Nostr and Bitcoin networks.

## Abstract

Nostr uses the same elliptic curve (secp256k1) as Bitcoin, making it possible to derive Bitcoin addresses directly from Nostr public keys. This NIP standardizes the process of deriving various Bitcoin address formats from Nostr public keys, enabling interoperability between Nostr and Bitcoin networks.

## Motivation

1. Enable direct Bitcoin payments to Nostr users without requiring additional key management
2. Create a bridge between Nostr's social layer and Bitcoin's payment layer
3. Simplify the process of accepting Bitcoin payments in Nostr applications
4. Enable automated Bitcoin address discovery for Nostr users

## Specification

### Public Key Conversion

1. Start with a Nostr public key in npub format (bech32-encoded)
2. Decode the npub using bech32 decoding
3. Convert the 5-bit data to 8-bit bytes
4. The resulting 32-byte hex string is the public key

### Bitcoin Address Derivation

From the public key, the following Bitcoin address types can be derived:

1. Legacy Address (P2PKH):
   - Apply SHA256 to the public key
   - Apply RIPEMD160 to the result
   - Add version byte (0x00 for mainnet)
   - Add checksum (first 4 bytes of double SHA256)
   - Encode in Base58

2. Native SegWit Address (P2WPKH):
   - Apply SHA256 to the public key
   - Apply RIPEMD160 to the result
   - Encode in bech32 format with "bc" prefix

3. Nested SegWit Address (P2SH-P2WPKH):
   - Apply SHA256 to the public key
   - Apply RIPEMD160 to the result
   - Create P2WPKH script
   - Apply SHA256 to the script
   - Apply RIPEMD160 to the result
   - Add version byte (0x05)
   - Add checksum
   - Encode in Base58

### Implementation Guidelines

1. Implementations MUST validate the input npub format
2. Implementations SHOULD support at least Legacy (P2PKH) addresses
3. Implementations MAY support additional address formats
4. Implementations SHOULD include clear warnings about address types and their implications

## Examples

```python
# Example conversion
npub = "npub12r0yjt8723ey2r035qtklhmdj90f0j6an7xnan8005jl7z5gw80qat9qrx"
hex_pubkey = "50de492cfe5472450df1a0176fdf6d915e97cb5d9f8d3eccef7d25ff0a8871de"
btc_address = "18smGGTPH9GNuNVbRAoCqm5BiU5yX86h1D"
```

## Reference Implementation

A reference implementation in Python is available at:
[npub_to_btc_converter.py](npub_to_btc_converter.py)

## Security Considerations

1. Address generation MUST be deterministic
2. Implementations SHOULD warn users about the permanence of blockchain transactions
3. Care should be taken when handling different address formats for different networks
4. Implementations should clearly indicate which network (mainnet/testnet) they are using

## Test Vectors

```python
[
    {
        "npub": "npub12r0yjt8723ey2r035qtklhmdj90f0j6an7xnan8005jl7z5gw80qat9qrx",
        "hex_pubkey": "50de492cfe5472450df1a0176fdf6d915e97cb5d9f8d3eccef7d25ff0a8871de",
        "legacy_address": "18smGGTPH9GNuNVbRAoCqm5BiU5yX86h1D"
    }
]
```

## Backwards Compatibility

This NIP is fully backwards compatible as it only adds functionality without modifying existing behavior.

## Client Support

Clients MAY implement this NIP to provide Bitcoin payment functionality to their users. The following features are recommended:

1. Display derived Bitcoin addresses alongside Nostr profiles
2. QR code generation for Bitcoin addresses
3. Clear indication of address format being used
4. Optional support for multiple address formats

## Implementation Status

This NIP is in draft status and is being implemented by:
- CornChat
- [List other implementations as they become available] 