# Implementation Plan: Optimizing Digital Forensic Security Via Secure Storage

A complete, production-grade final year project for Cyber Security / Digital Forensics that guarantees the **confidentiality, integrity, availability, and non-repudiation** of digital evidence through cryptographic optimization and an immutable Chain of Custody (CoC) ledger.

---

## User Review Required

> [!IMPORTANT]
> - The application will be built as a full-stack Python application (**FastAPI + Uvicorn + Modern Dark-Theme Cyber Forensic Web UI**), running natively on Python 3.14 without requiring Node.js.
> - Storage is organized into an **Encrypted Forensic Vault** with zero-knowledge AES-256-GCM encryption, dynamic chunking, zlib compression, and content-addressable deduplication.
> - An **Immutable Cryptographic Blockchain Ledger** will record every Chain-of-Custody event (Acquisition, Storage, Handover, Analysis, Verification) with SHA-256 block-linking and Merkle verification.

---

## System Architecture Overview

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                   FORENSIC WEB DASHBOARD (UI)                          │
 │  (Evidence Vault, Chain of Custody Visualizer, Verification, Audit)    │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ REST APIs & Streaming Upload
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                   FASTAPI APPLICATION BACKEND                          │
 │  ├── RBAC & Custodian Auth (Investigator, Analyst, Custodian, Court)   │
 │  ├── Evidence Ingestion Pipeline (Dual Hash: SHA-256 + BLAKE2b)        │
 │  └── Audit Verification & Court-Admissible Certificate Generator       │
 └─────────────────┬───────────────────────────────────┬──────────────────┘
                   │                                   │
                   ▼                                   ▼
 ┌───────────────────────────────────┐ ┌──────────────────────────────────┐
 │     OPTIMIZED STORAGE ENGINE      │ │    IMMUTABLE BLOCKCHAIN LEDGER   │
 │ ├── Content-Addressable Deduplication│ │ ├── Chronological Block Linking  │
 │ ├── Streaming Chunk Compression   │ │ ├── Merkle Tree Root Computation │
 │ ├── AES-256-GCM Envelope Crypto   │ │ ├── Cryptographic Digital Sigs   │
 │ └── Secure Local Forensic Vault   │ │ └── Real-time Tamper Detection   │
 └───────────────────────────────────┘ └──────────────────────────────────┘
```

---

## Proposed Changes

### Core Backend & Cryptographic Engine

#### [NEW] [config.py](file:///c:/Users/Vikas%20N/Desktop/Optimizing%20Digital%20Forensic%20Security%20Via%20Secure%20Storage/backend/config.py)
- Configuration for storage paths, vault keys, database settings, and forensic policies.

#### [NEW] [crypto_engine.py](file:///c:/Users/Vikas%20N/Desktop/Optimizing%20Digital%20Forensic%20Security%20Via%20Secure%20Storage/backend/crypto_engine.py)
- **Dual-Hashing Algorithm**: Generates SHA-256 and BLAKE2b digests upon ingestion to prevent collision attacks.
- **AES-256-GCM Hybrid Encryption**: Generates a cryptographically random 96-bit IV and 256-bit key per artifact, producing an authenticated 128-bit authentication tag.
- **Key Derivation (PBKDF2-HMAC-SHA256)**: Secure master key derivation with salt.

#### [NEW] [storage_optimizer.py](file:///c:/Users/Vikas%20N/Desktop/Optimizing%20Digital%20Forensic%20Security%20Via%20Secure%20Storage/backend/storage_optimizer.py)
- **Content-Addressable Deduplication**: Checks hash fingerprints before storing to eliminate redundant evidence storage (common in multi-device seizures).
- **Forensic Compression**: Compresses data before encryption (lossless) to optimize forensic disk capacity.
- **Secure Vault Manager**: Isolates encrypted evidence blobs from metadata.

#### [NEW] [blockchain_ledger.py](file:///c:/Users/Vikas%20N/Desktop/Optimizing%20Digital%20Forensic%20Security%20Via%20Secure%20Storage/backend/blockchain_ledger.py)
- **Forensic Block Structure**:
  - `block_index`, `timestamp`, `case_id`, `evidence_id`, `action` (SEIZED, STORED, TRANSFERRED, ACCESSED, VERIFIED), `custodian`, `evidence_hash`, `previous_hash`, `merkle_root`, `current_hash`.
- **Integrity Validation Engine**: Scans the entire ledger on-demand to detect any modified block or broken link.
- **Tamper Demonstration Mode**: Allows simulated tampering to demonstrate to evaluators how the blockchain instantly identifies tampered records.

#### [NEW] [models.py](file:///c:/Users/Vikas%20N/Desktop/Optimizing%20Digital%20Forensic%20Security%20Via%20Secure%20Storage/backend/models.py)
- Pydantic models for Evidence Ingestion, Custody Transfer, User Roles, and Forensic Audit Logs.

#### [NEW] [app.py](file:///c:/Users/Vikas%20N/Desktop/Optimizing%20Digital%20Forensic%20Security%20Via%20Secure%20Storage/backend/app.py)
- FastAPI entry point with API routes:
  - `/api/evidence/upload`: Secure ingestion, hashing, compression, encryption, and ledger block creation.
  - `/api/evidence/list`: Retrieve all logged evidence with storage optimization statistics.
  - `/api/evidence/verify/{id}`: Re-hashes encrypted vault content and compares with the ledger.
  - `/api/evidence/download/{id}`: Authenticated decryption and download with automated access logging.
  - `/api/ledger/blocks`: Returns the immutable chain of custody.
  - `/api/ledger/validate`: Runs complete cryptographic validation across all evidence and blocks.
  - `/api/ledger/tamper-test`: Evaluator demonstration endpoint.
  - `/api/certificate/{id}`: Generates a printable, court-admissible Chain of Custody certificate.

---

### Modern Cyber-Forensic Web Frontend

#### [NEW] [static/index.html](file:///c:/Users/Vikas%20N/Desktop/Optimizing%20Digital%20Forensic%20Security%20Via%20Secure%20Storage/static/index.html)
- Interactive Single Page Application (SPA) designed with a **Cyber-Forensic Glassmorphic Dark UI**:
  - **Overview Stats**: Total Evidence, Vault Size, Space Saved via Optimization (Deduplication & Compression Ratio), Ledger Integrity Status.
  - **Evidence Intake Portal**: Drag-and-drop file upload with case number, tag, investigator name, and classification level.
  - **Secure Evidence Vault**: Table of seized evidence with integrity indicators, encryption badges, and action buttons.
  - **Live Chain of Custody Timeline**: Visual block-by-block progression showing the full history of custody.
  - **Tamper Verification & Examiner Test Lab**: Live tool to verify evidence hashes and simulate tampering to prove detection capabilities.
  - **Court Certificate Modal**: Printable official Chain of Custody document for viva/project presentation.

#### [NEW] [static/css/styles.css](file:///c:/Users/Vikas%20N/Desktop/Optimizing%20Digital%20Forensic%20Security%20Via%20Secure%20Storage/static/css/styles.css)
- Custom high-tech styling: dark palette (`#0a0f1d`, `#111a2e`, `#00e5ff`, `#00ff9d`), smooth animations, badge indicators, responsive grid.

#### [NEW] [static/js/app.js](file:///c:/Users/Vikas%20N/Desktop/Optimizing%20Digital%20Forensic%20Security%20Via%20Secure%20Storage/static/js/app.js)
- Asynchronous API calls, real-time hash updates, dynamic modal rendering, and tamper simulation handlers.

---

### Project Documentation & Submission Kit

#### [NEW] [run.py](file:///c:/Users/Vikas%20N/Desktop/Optimizing%20Digital%20Forensic%20Security%20Via%20Secure%20Storage/run.py)
- One-click launcher script to start the server and open the browser.

#### [NEW] [PROJECT_DOCUMENTATION.md](file:///c:/Users/Vikas%20N/Desktop/Optimizing%20Digital%20Forensic%20Security%20Via%20Secure%20Storage/PROJECT_DOCUMENTATION.md)
- Complete Final Year Project documentation:
  - Abstract & Problem Statement
  - Literature Review & Existing System Limitations
  - Mathematical/Cryptographic Foundations (AES-256-GCM, Merkle Trees, SHA-256)
  - System Architecture & Data Flow Diagrams
  - Storage Optimization Analysis (Storage savings formulas)
  - Step-by-step Viva / Demonstration Guide for examiners

---

## Verification Plan

### Automated Tests
1. **Cryptographic Integrity Test**: Ingest a sample forensic file, record SHA-256 and BLAKE2b, encrypt into vault, decrypt, and confirm hash matching.
2. **Storage Optimization Test**: Upload identical files to verify deduplication index; upload compressible text/logs to verify compression ratio.
3. **Chain of Custody Ledger Test**: Append 5 distinct custody events, run integrity validator (must return 100% valid).
4. **Tamper Detection Test**: Intentionally alter 1 byte in a vault file or ledger entry, rerun validation, verify that the system flags the exact block as compromised.

### Manual Verification
1. Launch the server using `python run.py`.
2. Access the UI at `http://127.0.0.1:8000`.
3. Ingest a test forensic file (e.g. disk image / pcap / document).
4. Inspect the Chain of Custody visual timeline.
5. Click **Verify Integrity** and check real-time dual-hash verification.
6. Generate and preview the printable **Court-Admissible Evidence Certificate**.
