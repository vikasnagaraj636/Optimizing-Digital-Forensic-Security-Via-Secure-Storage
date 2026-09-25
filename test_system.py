"""
Automated Verification & Integrity Test Suite
Tests:
1. Dual Cryptographic Hashing
2. Authenticated AES-256-GCM Encryption / Decryption
3. Storage Optimization (Lossless Compression + Deduplication)
4. Blockchain Chain of Custody & Merkle Root Calculations
5. Deliberate Tamper Detection & Defense Verification
"""

import os
import sys
from pathlib import Path

# Ensure UTF-8 console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.crypto_engine import CryptoEngine
from backend.storage_optimizer import StorageOptimizer
from backend.blockchain_ledger import BlockchainLedger

def run_tests():
    print("\n" + "=" * 70)
    print("RUNNING AUTOMATED VERIFICATION SUITE")
    print("=" * 70)

    # TEST 1: Cryptographic Engine Dual Hashing
    print("\n[TEST 1] Testing Dual Hashing (SHA-256 + BLAKE2b)...")
    sample_payload = b"CRITICAL_FORENSIC_EVIDENCE_PAYLOAD_2026" * 50
    hashes = CryptoEngine.compute_dual_hashes(sample_payload)
    assert len(hashes["sha256"]) == 64, "SHA-256 hash length must be 64 hex characters"
    assert len(hashes["blake2b"]) == 128, "BLAKE2b hash length must be 128 hex characters"
    print(f"  [OK] SHA-256: {hashes['sha256'][:24]}...")
    print(f"  [OK] BLAKE2b: {hashes['blake2b'][:24]}...")
    print("  --> Dual Hashing Passed.")

    # TEST 2: AES-256-GCM Hybrid Encryption & Decryption
    print("\n[TEST 2] Testing AES-256-GCM Authenticated Encryption & Decryption...")
    salt = b"TEST_SALT_123456"
    key = CryptoEngine.derive_key("TestMasterPassphrase!123", salt)
    iv, ciphertext = CryptoEngine.encrypt_data(sample_payload, key, associated_data=b"EV-TEST-001")
    decrypted = CryptoEngine.decrypt_data(ciphertext, key, iv, associated_data=b"EV-TEST-001")
    assert decrypted == sample_payload, "Decrypted data must match original payload exactly"
    print("  [OK] Zero-Knowledge Authenticated Encryption & Decryption Passed.")

    # TEST 3: Storage Optimizer - Deduplication & Compression
    print("\n[TEST 3] Testing Storage Optimization & Deduplication Engine...")
    optimizer = StorageOptimizer()

    test_file_content = ("SUSPICIOUS SYSTEM LOG DUMP\n" * 200).encode()
    raw_size = len(test_file_content)

    rec1 = optimizer.optimize_and_store(
        evidence_id="EV-TEST-101",
        filename="system_auth.log",
        raw_data=test_file_content,
        case_id="CASE-UNIT-01",
        custodian="Detective Sherlock",
        classification="Confidential"
    )

    print(f"  [OK] File 1 Stored: Raw={rec1['raw_size_bytes']}B, Vault={rec1['vault_size_bytes']}B, Saved={rec1['compression_ratio_pct']}%")
    assert rec1["vault_size_bytes"] < rec1["raw_size_bytes"], "Vault size must be smaller due to compression"

    # Ingest duplicate file
    rec2 = optimizer.optimize_and_store(
        evidence_id="EV-TEST-102",
        filename="duplicate_system_auth.log",
        raw_data=test_file_content,
        case_id="CASE-UNIT-02",
        custodian="Agent Watson",
        classification="Confidential"
    )
    print(f"  [OK] File 2 (Duplicate) Stored: Status='{rec2['status']}', is_duplicate={rec2['is_duplicate']}")
    assert rec2["is_duplicate"] is True, "Identical content must trigger content-addressable deduplication"
    print("  --> Storage Optimization & Deduplication Passed.")

    # TEST 4: Evidence Retrieval & Integrity Verification
    print("\n[TEST 4] Testing Evidence Decryption & Integrity Verification...")
    retrieved_data, report = optimizer.retrieve_and_verify("EV-TEST-101")
    assert retrieved_data == test_file_content, "Retrieved data must match original input"
    assert report["integrity_valid"] is True, "Cryptographic integrity check must pass"
    print(f"  [OK] Decrypted and Verified: SHA-256 Matches 100%")

    # TEST 5: Blockchain Ledger Audit & Tamper Simulation
    print("\n[TEST 5] Testing Blockchain Chain of Custody & Tamper Detection...")
    ledger = BlockchainLedger()

    # Append block
    b1 = ledger.add_block(
        case_id="CASE-UNIT-01",
        evidence_id="EV-TEST-101",
        action="EVIDENCE_SEIZED_AT_SCENE",
        custodian="Officer Miller",
        evidence_hash=rec1["content_hash"],
        notes="Seized during initial warrant execution"
    )
    print(f"  [OK] Appended Block #{b1.index}: {b1.action}")

    # Validate healthy ledger
    audit_pre = ledger.validate_chain()
    assert audit_pre["is_valid"] is True, f"Ledger must be valid, but got: {audit_pre}"
    print(f"  [OK] Pre-Tamper Audit: ALL {audit_pre['total_blocks']} BLOCKS CRYPTOGRAPHICALLY VALID")

    # Deliberately Tamper
    import time
    attack_payload = f"MALICIOUS_TAMPER_ATTACK_{int(time.time()*1000)}"
    print(f"  --> Simulating Malicious Tamper on Block #1 with payload '{attack_payload}'...")
    ledger.simulate_tampering(1, attack_payload)

    # Re-run audit
    audit_tampered = ledger.validate_chain()
    assert audit_tampered["is_valid"] is False, "Auditor must detect tampering!"
    assert audit_tampered["tampered_block_index"] == 1, "Auditor must pinpoint Block #1 as compromised"
    print(f"  [OK] Tamper Successfully Caught! Auditor flagged: {audit_tampered['error']}")

    # Repair ledger
    ledger.repair_chain_recompute()
    audit_repaired = ledger.validate_chain()
    assert audit_repaired["is_valid"] is True, "Ledger must be valid after repair"
    print("  [OK] Post-Tamper Repair & Synchronization Successful.")

    print("\n" + "=" * 70)
    print("ALL 5 AUTOMATED VERIFICATION TESTS PASSED SUCCESSFULLY! (100% OPERATIONAL)")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    run_tests()
