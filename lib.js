// Noble-secp256k1 library (minimal version for our needs)
const secp256k1 = {
    Point: class {
        static fromHex(hex) {
            // This is a simplified version - in production use the full noble-secp256k1 library
            return {
                toRawBytes: (compressed = true) => {
                    // Return a dummy compressed public key
                    return new Uint8Array(33);
                }
            };
        }
    }
};

// Bech32 implementation
const bech32 = {
    // Encoding constants
    CHARSET: 'qpzry9x8gf2tvdw0s3jn54khce6mua7l',
    GENERATOR: [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3],
    
    // Main encoding/decoding functions
    encode: function(hrp, data) {
        const checksum = this.createChecksum(hrp, data);
        const combined = data.concat(checksum);
        let ret = hrp + '1';
        for (let p = 0; p < combined.length; p++) {
            ret += this.CHARSET.charAt(combined[p]);
        }
        return ret;
    },
    
    decode: function(bechString) {
        if (!bechString.match(/^[a-z0-9]+$/i)) {
            throw new Error('Invalid character in bech32 string');
        }
        
        const lowered = bechString.toLowerCase();
        const pos = lowered.lastIndexOf('1');
        if (pos < 1 || pos + 7 > lowered.length || lowered.length > 90) {
            throw new Error('Invalid bech32 string');
        }
        
        const hrp = lowered.substring(0, pos);
        const data = [];
        for (let p = pos + 1; p < lowered.length; p++) {
            const d = this.CHARSET.indexOf(lowered.charAt(p));
            if (d === -1) {
                throw new Error('Invalid character in bech32 string');
            }
            data.push(d);
        }
        
        if (!this.verifyChecksum(hrp, data)) {
            throw new Error('Invalid bech32 checksum');
        }
        
        return {
            hrp: hrp,
            words: data.slice(0, -6)
        };
    },
    
    createChecksum: function(hrp, data) {
        const values = this.hrpExpand(hrp).concat(data).concat([0, 0, 0, 0, 0, 0]);
        const mod = this.polymod(values) ^ 1;
        const ret = [];
        for (let p = 0; p < 6; p++) {
            ret.push((mod >> 5 * (5 - p)) & 31);
        }
        return ret;
    },
    
    verifyChecksum: function(hrp, data) {
        return this.polymod(this.hrpExpand(hrp).concat(data)) === 1;
    },
    
    hrpExpand: function(hrp) {
        const ret = [];
        for (let p = 0; p < hrp.length; p++) {
            ret.push(hrp.charCodeAt(p) >> 5);
        }
        ret.push(0);
        for (let p = 0; p < hrp.length; p++) {
            ret.push(hrp.charCodeAt(p) & 31);
        }
        return ret;
    },
    
    polymod: function(values) {
        let chk = 1;
        for (let p = 0; p < values.length; p++) {
            const top = chk >> 25;
            chk = (chk & 0x1ffffff) << 5 ^ values[p];
            for (let i = 0; i < 5; i++) {
                if ((top >> i) & 1) {
                    chk ^= this.GENERATOR[i];
                }
            }
        }
        return chk;
    },
    
    // Convert between 5-bit and 8-bit arrays
    toWords: function(bytes) {
        const ret = [];
        let acc = 0;
        let bits = 0;
        for (const b of bytes) {
            acc = (acc << 8) | b;
            bits += 8;
            while (bits >= 5) {
                bits -= 5;
                ret.push((acc >> bits) & 31);
            }
        }
        if (bits > 0) {
            ret.push((acc << (5 - bits)) & 31);
        }
        return ret;
    },
    
    fromWords: function(words) {
        const ret = [];
        let acc = 0;
        let bits = 0;
        for (const w of words) {
            acc = (acc << 5) | w;
            bits += 5;
            while (bits >= 8) {
                bits -= 8;
                ret.push((acc >> bits) & 255);
            }
        }
        return new Uint8Array(ret);
    }
};

// RIPEMD160 implementation
function ripemd160(buffer) {
    // This is a simplified version that returns a dummy hash
    // In production, use a proper RIPEMD160 implementation
    return new Uint8Array(20).fill(0);
}

// Export the libraries
window.secp256k1 = secp256k1;
window.bech32 = bech32;
window.ripemd160 = ripemd160; 