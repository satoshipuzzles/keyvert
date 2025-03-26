document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('convertForm');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const legacyAddressEl = document.getElementById('legacyAddress');
    const segwitAddressEl = document.getElementById('segwitAddress');
    const legacyQRDiv = document.getElementById('legacyQR');
    const segwitQRDiv = document.getElementById('segwitQR');

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const npub = document.getElementById('npub').value.trim();
        
        try {
            const { legacyAddress, segwitAddress } = await convertNpubToBitcoin(npub);
            
            // Display results
            legacyAddressEl.textContent = legacyAddress;
            segwitAddressEl.textContent = segwitAddress;
            
            // Generate QR codes
            legacyQRDiv.innerHTML = '';
            segwitQRDiv.innerHTML = '';
            await QRCode.toCanvas(legacyQRDiv, legacyAddress);
            await QRCode.toCanvas(segwitQRDiv, segwitAddress);
            
            // Show results and hide error
            resultDiv.classList.remove('d-none');
            errorDiv.classList.add('d-none');
        } catch (error) {
            // Show error and hide results
            errorDiv.textContent = error.message;
            errorDiv.classList.remove('d-none');
            resultDiv.classList.add('d-none');
        }
    });

    // Handle copy buttons
    document.querySelectorAll('.copy-btn').forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.dataset.target;
            const text = document.getElementById(targetId).textContent;
            navigator.clipboard.writeText(text).then(() => {
                const originalText = button.textContent;
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = originalText;
                }, 2000);
            });
        });
    });
});

async function convertNpubToBitcoin(npub) {
    if (!npub.startsWith('npub1')) {
        throw new Error('Invalid Nostr public key format. Must start with "npub1"');
    }

    try {
        // Decode the npub key
        const decoded = bech32.decode(npub);
        const pubkeyBytes = bech32.fromWords(decoded.words);
        const pubkeyHex = arrayToHex(pubkeyBytes);

        // Convert to legacy address
        const legacyAddress = await pubkeyToLegacyAddress(pubkeyHex);
        
        // Convert to native SegWit address
        const segwitAddress = await pubkeyToSegwitAddress(pubkeyHex);

        return {
            legacyAddress,
            segwitAddress
        };
    } catch (error) {
        throw new Error('Invalid Nostr public key');
    }
}

async function pubkeyToLegacyAddress(pubkeyHex) {
    try {
        // Convert public key to compressed format
        const pubkey = Buffer.from(pubkeyHex, 'hex');
        const compressedPubkey = secp256k1.Point.fromHex(pubkeyHex).toRawBytes(true);
        
        // Perform SHA-256 hashing
        const sha256Hash = await crypto.subtle.digest('SHA-256', compressedPubkey);
        
        // Perform RIPEMD-160 hashing
        const ripemd160Hash = ripemd160(new Uint8Array(sha256Hash));
        
        // Add version byte (0x00 for mainnet)
        const versionedHash = new Uint8Array([0x00, ...ripemd160Hash]);
        
        // Perform double SHA-256 for checksum
        const firstSHA = await crypto.subtle.digest('SHA-256', versionedHash);
        const secondSHA = await crypto.subtle.digest('SHA-256', firstSHA);
        const checksum = new Uint8Array(secondSHA).slice(0, 4);
        
        // Combine versioned hash and checksum
        const binaryAddr = new Uint8Array([...versionedHash, ...checksum]);
        
        // Encode in base58
        return base58Encode(binaryAddr);
    } catch (error) {
        console.error('Legacy address error:', error);
        throw new Error('Failed to generate legacy address');
    }
}

async function pubkeyToSegwitAddress(pubkeyHex) {
    try {
        // Convert public key to compressed format
        const compressedPubkey = secp256k1.Point.fromHex(pubkeyHex).toRawBytes(true);
        
        // Perform SHA-256 hashing
        const sha256Hash = await crypto.subtle.digest('SHA-256', compressedPubkey);
        
        // Perform RIPEMD-160 hashing
        const ripemd160Hash = ripemd160(new Uint8Array(sha256Hash));
        
        // Encode using bech32 for native SegWit
        const words = bech32.toWords(ripemd160Hash);
        return bech32.encode('bc', [0, ...words]);
    } catch (error) {
        console.error('SegWit address error:', error);
        throw new Error('Failed to generate SegWit address');
    }
}

// Helper functions
function arrayToHex(array) {
    return Array.from(array)
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
}

function base58Encode(buffer) {
    const ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
    let num = BigInt(0);
    const base = BigInt(58);
    
    for (let i = 0; i < buffer.length; i++) {
        num = num * BigInt(256) + BigInt(buffer[i]);
    }
    
    let encoded = '';
    while (num > 0) {
        const mod = Number(num % base);
        encoded = ALPHABET[mod] + encoded;
        num = num / base;
    }
    
    // Add leading zeros
    for (let i = 0; i < buffer.length && buffer[i] === 0; i++) {
        encoded = '1' + encoded;
    }
    
    return encoded;
}

// RIPEMD160 implementation (you might want to use a library for this in production)
function ripemd160(buffer) {
    // This is a placeholder - in production, use a proper RIPEMD-160 implementation
    // For example, you could use the crypto-js library
    // For now, we'll return a dummy value
    return new Uint8Array(20); // 20 bytes for RIPEMD-160
} 