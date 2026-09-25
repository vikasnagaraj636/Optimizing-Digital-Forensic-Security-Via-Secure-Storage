import json
import zlib
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from backend.config import VAULT_DIR, METADATA_FILE, KEYS_FILE, DEFAULT_MASTER_KEY
from backend.crypto_engine import CryptoEngine

class StorageOptimizer:
    """
    Forensic Storage Optimizer:
    1. Content-addressable Deduplication (Identical hashes reference existing vault blobs)
    2. Lossless compression (reduces forensic disk footprint)
    3. Authenticated AES-256-GCM zero-knowledge vault storage
    4. Tracks storage optimization metrics (savings ratio, compression ratio)
    """

    def __init__(self):
        self.metadata_file = METADATA_FILE
        self.keys_file = KEYS_FILE
        self.vault_dir = VAULT_DIR
        self._init_files()

    def _init_files(self):
        if not self.metadata_file.exists():
            self._save_json(self.metadata_file, {})
        if not self.keys_file.exists():
            self._save_json(self.keys_file, {})

    def _read_json(self, path: Path) -> Dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_json(self, path: Path, data: Dict[str, Any]):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def optimize_and_store(
        self,
        evidence_id: str,
        filename: str,
        raw_data: bytes,
        case_id: str,
        custodian: str,
        classification: str
    ) -> Dict[str, Any]:
        """
        Processes forensic evidence:
        - Computes dual cryptographic digests
        - Deduplication check against existing vault blobs
        - If new: Compresses -> Derives key -> Encrypts with AES-256-GCM -> Saves to Vault
        - Updates metadata and key repository
        """
        raw_size = len(raw_data)
        hashes = CryptoEngine.compute_dual_hashes(raw_data)
        content_hash = hashes["sha256"]

        metadata = self._read_json(self.metadata_file)
        keys = self._read_json(self.keys_file)

        # 1. Content-Addressable Deduplication Check
        vault_filename = f"{content_hash}.vault"
        vault_path = self.vault_dir / vault_filename
        is_duplicate = vault_path.exists() and content_hash in keys

        if is_duplicate:
            existing_key_meta = keys[content_hash]
            compressed_size = existing_key_meta["compressed_size"]
            vault_size = existing_key_meta["vault_size"]
            dedup_savings = raw_size
            status = "Deduplicated (Referenced Existing Vault Blob)"
        else:
            # 2. Lossless Compression (Level 9 for maximum storage optimization)
            compressed_data = zlib.compress(raw_data, level=9)
            compressed_size = len(compressed_data)

            # 3. Key Generation & Derivation
            salt = Path(vault_filename).name.encode()[:16].ljust(16, b"F")
            key = CryptoEngine.derive_key(DEFAULT_MASTER_KEY, salt)

            # 4. Authenticated AES-256-GCM Encryption
            iv, ciphertext = CryptoEngine.encrypt_data(
                compressed_data,
                key,
                associated_data=evidence_id.encode()
            )
            vault_size = len(iv) + len(ciphertext)

            # Store encrypted blob in vault: [12-byte IV] + [Ciphertext + Tag]
            with open(vault_path, "wb") as vf:
                vf.write(iv + ciphertext)

            # Record vault blob encryption parameters
            keys[content_hash] = {
                "salt_hex": salt.hex(),
                "iv_hex": iv.hex(),
                "vault_file": vault_filename,
                "raw_size": raw_size,
                "compressed_size": compressed_size,
                "vault_size": vault_size
            }
            self._save_json(self.keys_file, keys)
            dedup_savings = 0
            status = "Stored (Compressed & Encrypted)"

        # Calculate space optimization metrics
        space_saved = max(0, raw_size - vault_size) if not is_duplicate else raw_size
        compression_ratio = round((1 - (compressed_size / raw_size)) * 100, 2) if raw_size > 0 else 0.0
        overall_reduction = round((1 - (vault_size / raw_size)) * 100, 2) if raw_size > 0 and not is_duplicate else (100.0 if is_duplicate else 0.0)

        record = {
            "evidence_id": evidence_id,
            "case_id": case_id,
            "filename": filename,
            "classification": classification,
            "custodian": custodian,
            "content_hash": content_hash,
            "blake2b_hash": hashes["blake2b"],
            "vault_file": vault_filename,
            "raw_size_bytes": raw_size,
            "compressed_size_bytes": compressed_size,
            "vault_size_bytes": vault_size,
            "space_saved_bytes": space_saved,
            "compression_ratio_pct": compression_ratio,
            "overall_reduction_pct": overall_reduction,
            "is_duplicate": is_duplicate,
            "status": status
        }

        metadata[evidence_id] = record
        self._save_json(self.metadata_file, metadata)

        return record

    def retrieve_and_verify(self, evidence_id: str) -> Tuple[Optional[bytes], Dict[str, Any]]:
        """
        Retrieves evidence from the vault, decrypts, decompresses,
        and cryptographically re-verifies against stored dual-hashes.
        """
        metadata = self._read_json(self.metadata_file)
        if evidence_id not in metadata:
            return None, {"error": "Evidence ID not found in metadata repository"}

        meta = metadata[evidence_id]
        content_hash = meta["content_hash"]
        keys = self._read_json(self.keys_file)

        if content_hash not in keys:
            return None, {"error": "Encryption keys not found for evidence"}

        key_info = keys[content_hash]
        vault_path = self.vault_dir / key_info["vault_file"]

        if not vault_path.exists():
            return None, {"error": f"Physical vault file {key_info['vault_file']} missing or deleted!"}

        with open(vault_path, "rb") as vf:
            raw_vault_bytes = vf.read()

        iv = raw_vault_bytes[:12]
        ciphertext = raw_vault_bytes[12:]

        salt = bytes.fromhex(key_info["salt_hex"])
        key = CryptoEngine.derive_key(DEFAULT_MASTER_KEY, salt)

        try:
            # Authenticated Decryption
            compressed_data = CryptoEngine.decrypt_data(
                ciphertext,
                key,
                iv,
                associated_data=evidence_id.encode()
            )
            # Lossless Decompression
            original_data = zlib.decompress(compressed_data)
        except Exception as e:
            return None, {
                "error": f"CRYPTOGRAPHIC TAMPER DETECTED! Authentication tag verification failed: {str(e)}",
                "tampered": True
            }

        # Verify integrity of recovered data
        recomputed_hashes = CryptoEngine.compute_dual_hashes(original_data)
        integrity_valid = (recomputed_hashes["sha256"] == meta["content_hash"]) and (recomputed_hashes["blake2b"] == meta["blake2b_hash"])

        return original_data, {
            "evidence_id": evidence_id,
            "filename": meta["filename"],
            "integrity_valid": integrity_valid,
            "stored_sha256": meta["content_hash"],
            "recomputed_sha256": recomputed_hashes["sha256"],
            "stored_blake2b": meta["blake2b_hash"],
            "recomputed_blake2b": recomputed_hashes["blake2b"],
            "tampered": not integrity_valid
        }

    def get_all_metadata(self) -> Dict[str, Any]:
        return self._read_json(self.metadata_file)

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Computes global storage savings, deduplication, and compression efficiency."""
        metadata = self._read_json(self.metadata_file)
        keys = self._read_json(self.keys_file)

        total_raw = sum(item.get("raw_size_bytes", 0) for item in metadata.values())
        unique_vault_size = sum(k.get("vault_size", 0) for k in keys.values())
        total_items = len(metadata)
        unique_blobs = len(keys)
        dedup_count = sum(1 for item in metadata.values() if item.get("is_duplicate"))

        total_saved = max(0, total_raw - unique_vault_size)
        total_saving_pct = round((total_saved / total_raw) * 100, 2) if total_raw > 0 else 0.0

        return {
            "total_evidence_count": total_items,
            "unique_vault_blobs": unique_blobs,
            "deduplicated_files": dedup_count,
            "total_uncompressed_bytes": total_raw,
            "total_vault_stored_bytes": unique_vault_size,
            "total_bytes_saved": total_saved,
            "storage_reduction_percentage": total_saving_pct
        }
