import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Tuple
from backend.config import LEDGER_FILE
from backend.crypto_engine import CryptoEngine

class ForensicBlock:
    def __init__(
        self,
        index: int,
        timestamp: str,
        case_id: str,
        evidence_id: str,
        action: str,
        custodian: str,
        evidence_hash: str,
        previous_hash: str,
        notes: str = "",
        recipient: str = "",
        merkle_root: str = "",
        block_hash: str = ""
    ):
        self.index = index
        self.timestamp = timestamp
        self.case_id = case_id
        self.evidence_id = evidence_id
        self.action = action  # e.g., EVIDENCE_SEIZED, VAULT_STORED, CUSTODY_TRANSFERRED, ANALYST_CHECKOUT, FORENSIC_VERIFIED
        self.custodian = custodian
        self.recipient = recipient
        self.notes = notes
        self.evidence_hash = evidence_hash
        self.previous_hash = previous_hash
        self.merkle_root = merkle_root
        self.block_hash = block_hash or self.compute_hash()

    def compute_hash(self) -> str:
        """Computes the SHA-256 block hash over all block data."""
        payload = (
            f"{self.index}|{self.timestamp}|{self.case_id}|{self.evidence_id}|"
            f"{self.action}|{self.custodian}|{self.recipient}|{self.notes}|"
            f"{self.evidence_hash}|{self.previous_hash}|{self.merkle_root}"
        )
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "case_id": self.case_id,
            "evidence_id": self.evidence_id,
            "action": self.action,
            "custodian": self.custodian,
            "recipient": self.recipient,
            "notes": self.notes,
            "evidence_hash": self.evidence_hash,
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "block_hash": self.block_hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ForensicBlock':
        return cls(
            index=data["index"],
            timestamp=data["timestamp"],
            case_id=data["case_id"],
            evidence_id=data["evidence_id"],
            action=data["action"],
            custodian=data["custodian"],
            recipient=data.get("recipient", ""),
            notes=data.get("notes", ""),
            evidence_hash=data["evidence_hash"],
            previous_hash=data["previous_hash"],
            merkle_root=data.get("merkle_root", ""),
            block_hash=data.get("block_hash", "")
        )


class BlockchainLedger:
    """
    Cryptographic immutable ledger maintaining the digital forensic Chain of Custody (CoC).
    Features:
    - Block linking via cryptographic SHA-256 hashes
    - Real-time Merkle Root maintenance
    - Rigorous full-chain integrity auditing
    - Forensic tamper simulation & detection for academic demonstrations
    """

    def __init__(self):
        self.ledger_file = LEDGER_FILE
        self.chain: List[ForensicBlock] = []
        self._load_or_create_chain()

    def _load_or_create_chain(self):
        if self.ledger_file.exists():
            try:
                with open(self.ledger_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.chain = [ForensicBlock.from_dict(b) for b in data]
                    if self.chain:
                        return
            except Exception:
                self.chain = []

        # Initialize Genesis Block if new
        genesis_block = ForensicBlock(
            index=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
            case_id="SYSTEM_ROOT",
            evidence_id="GENESIS_EVIDENCE_ROOT",
            action="GENESIS_INITIALIZATION",
            custodian="Digital Forensic Authority System",
            evidence_hash=hashlib.sha256(b"DIGITAL_FORENSIC_GENESIS_ROOT").hexdigest(),
            previous_hash="0" * 64,
            notes="Root anchor for secure forensic evidence storage ledger",
            merkle_root=hashlib.sha256(b"DIGITAL_FORENSIC_GENESIS_ROOT").hexdigest()
        )
        self.chain = [genesis_block]
        self._save_chain()

    def _save_chain(self):
        with open(self.ledger_file, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=2)

    def get_latest_block(self) -> ForensicBlock:
        return self.chain[-1]

    def add_block(
        self,
        case_id: str,
        evidence_id: str,
        action: str,
        custodian: str,
        evidence_hash: str,
        notes: str = "",
        recipient: str = ""
    ) -> ForensicBlock:
        """Appends a new verified event block to the Chain of Custody."""
        latest = self.get_latest_block()
        new_index = latest.index + 1
        timestamp = datetime.now(timezone.utc).isoformat()
        prev_hash = latest.block_hash

        # Collect all evidence hashes in chain to form current Merkle Root
        all_hashes = [b.evidence_hash for b in self.chain] + [evidence_hash]
        merkle_root = CryptoEngine.compute_merkle_root(all_hashes)

        new_block = ForensicBlock(
            index=new_index,
            timestamp=timestamp,
            case_id=case_id,
            evidence_id=evidence_id,
            action=action,
            custodian=custodian,
            recipient=recipient,
            notes=notes,
            evidence_hash=evidence_hash,
            previous_hash=prev_hash,
            merkle_root=merkle_root
        )

        self.chain.append(new_block)
        self._save_chain()
        return new_block

    def get_evidence_history(self, evidence_id: str) -> List[Dict[str, Any]]:
        """Retrieves all chronological custody events for a specific evidence item."""
        return [b.to_dict() for b in self.chain if b.evidence_id == evidence_id or b.index == 0]

    def get_all_blocks(self) -> List[Dict[str, Any]]:
        return [b.to_dict() for b in self.chain]

    def validate_chain(self) -> Dict[str, Any]:
        """
        Performs exhaustive cryptographic audit on the ledger:
        1. Genesis block integrity
        2. Block hash matching computed hash
        3. Previous hash linking
        4. Merkle root consistency
        """
        # Reload from disk to detect external modifications
        self._load_or_create_chain()

        if not self.chain:
            return {"is_valid": False, "error": "Ledger is empty", "tampered_block_index": 0}

        all_hashes = []
        for i, block in enumerate(self.chain):
            all_hashes.append(block.evidence_hash)

            # 1. Verify computed block hash matches recorded block hash
            expected_hash = block.compute_hash()
            if block.block_hash != expected_hash:
                return {
                    "is_valid": False,
                    "error": f"BLOCK CORRUPTION DETECTED at Block #{block.index}: Hash mismatch!",
                    "tampered_block_index": block.index,
                    "expected_hash": expected_hash,
                    "actual_hash": block.block_hash
                }

            # 2. Verify previous hash link (except genesis)
            if i > 0:
                prev_block = self.chain[i - 1]
                if block.previous_hash != prev_block.block_hash:
                    return {
                        "is_valid": False,
                        "error": f"CHAIN BROKEN at Block #{block.index}: Previous hash link mismatch!",
                        "tampered_block_index": block.index,
                        "expected_prev_hash": prev_block.block_hash,
                        "actual_prev_hash": block.previous_hash
                    }

            # 3. Verify Merkle root
            expected_merkle = CryptoEngine.compute_merkle_root(all_hashes)
            if block.merkle_root != expected_merkle:
                return {
                    "is_valid": False,
                    "error": f"MERKLE TREE ROOT INVALID at Block #{block.index}: Evidence history has been modified!",
                    "tampered_block_index": block.index,
                    "expected_merkle": expected_merkle,
                    "actual_merkle": block.merkle_root
                }

        return {
            "is_valid": True,
            "total_blocks": len(self.chain),
            "latest_block_hash": self.chain[-1].block_hash,
            "latest_merkle_root": self.chain[-1].merkle_root,
            "status": "ALL_BLOCKS_CRYPTOGRAPHICALLY_VERIFIED"
        }

    def simulate_tampering(self, block_index: int, malicious_action: str = "TAMPERED_MODIFIED_EVIDENCE") -> Dict[str, Any]:
        """
        Educational/Demonstration tool for final year project defense:
        Simulates an unauthorized attacker directly modifying the ledger file on disk,
        demonstrating the cryptographic detection response.
        """
        if block_index < 0 or block_index >= len(self.chain):
            return {"error": "Invalid block index"}

        with open(self.ledger_file, "r", encoding="utf-8") as f:
            raw_blocks = json.load(f)

        # Alter the block data without re-computing the cryptographic hash
        raw_blocks[block_index]["action"] = malicious_action
        raw_blocks[block_index]["notes"] = "ATTACKER INJECTION: Evidence compromised via unauthorized direct file alteration"

        with open(self.ledger_file, "w", encoding="utf-8") as f:
            json.dump(raw_blocks, f, indent=2)

        return {
            "tampered_block_index": block_index,
            "simulated_action": malicious_action,
            "message": "Block intentionally tampered on storage disk. Run audit to observe detection."
        }

    def repair_chain_recompute(self) -> Dict[str, Any]:
        """Recalculates all hashes and Merkle roots to restore valid ledger state after demo."""
        self._load_or_create_chain()
        all_hashes = []
        for i, block in enumerate(self.chain):
            all_hashes.append(block.evidence_hash)
            if i > 0:
                block.previous_hash = self.chain[i - 1].block_hash
            block.merkle_root = CryptoEngine.compute_merkle_root(all_hashes)
            block.block_hash = block.compute_hash()

        self._save_chain()
        return {"status": "REPAIRED_AND_SYNCHRONIZED", "total_blocks": len(self.chain)}
