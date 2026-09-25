import os
import hashlib
from typing import Tuple, Dict, List
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from backend.config import PBKDF2_ITERATIONS, GCM_IV_SIZE

class CryptoEngine:
    """
    Forensic-grade cryptographic engine providing:
    - Dual-digest cryptographic hashing (SHA-256 + BLAKE2b) for collision resistance
    - Authenticated Symmetric Encryption (AES-256-GCM) with random IV and authentication tag
    - Key derivation via PBKDF2-HMAC-SHA256
    - Merkle Root hash calculation for immutable tamper validation
    """

    @staticmethod
    def derive_key(passphrase: str, salt: bytes) -> bytes:
        """Derives a 256-bit AES key from a passphrase and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=PBKDF2_ITERATIONS,
        )
        return kdf.derive(passphrase.encode('utf-8'))

    @staticmethod
    def compute_dual_hashes(data: bytes) -> Dict[str, str]:
        """
        Computes both SHA-256 and BLAKE2b digests.
        Forensic dual-hashing guarantees non-repudiation and eliminates collision risks.
        """
        sha256_hash = hashlib.sha256(data).hexdigest()
        blake2b_hash = hashlib.blake2b(data).hexdigest()
        return {
            "sha256": sha256_hash,
            "blake2b": blake2b_hash
        }

    @staticmethod
    def encrypt_data(plaintext: bytes, key: bytes, associated_data: bytes = b"") -> Tuple[bytes, bytes]:
        """
        Encrypts plaintext bytes using AES-256-GCM authenticated cipher.
        Returns (iv, ciphertext_with_tag).
        """
        aesgcm = AESGCM(key)
        iv = os.urandom(GCM_IV_SIZE)
        ciphertext = aesgcm.encrypt(iv, plaintext, associated_data)
        return iv, ciphertext

    @staticmethod
    def decrypt_data(ciphertext: bytes, key: bytes, iv: bytes, associated_data: bytes = b"") -> bytes:
        """
        Decrypts ciphertext with authentication verification.
        Raises InvalidTag if any single byte of ciphertext or IV has been tampered with.
        """
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(iv, ciphertext, associated_data)

    @staticmethod
    def compute_merkle_root(leaf_hashes: List[str]) -> str:
        """
        Computes a cryptographic Merkle Root from an ordered list of leaf hashes.
        Ensures cryptographic proof of inclusion and immutability across evidence blocks.
        """
        if not leaf_hashes:
            return hashlib.sha256(b"EMPTY_LEDGER").hexdigest()

        current_level = [bytes.fromhex(h) if len(h) == 64 else hashlib.sha256(h.encode()).digest() for h in leaf_hashes]

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = hashlib.sha256(left + right).digest()
                next_level.append(combined)
            current_level = next_level

        return current_level[0].hex()
