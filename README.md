# Optimizing Digital Forensic Security Via Secure Storage
### Final Year Capstone Project (2025 - 2026)

A full-stack, forensic-grade digital evidence security and storage optimization system featuring:
- **Dual Cryptographic Hashing**: SHA-256 + BLAKE2b
- **Zero-Knowledge Authenticated Encryption**: AES-256-GCM with unique IVs and PBKDF2 key derivation
- **Forensic Storage Optimization**: Content-addressable deduplication & lossless compression
- **Immutable Chain of Custody**: Cryptographic Merkle-blockchain ledger
- **Tamper Detection Lab**: Interactive examiner demonstration showing automated isolation of compromised records
- **Court Admissibility**: Printable Chain of Custody certificates compliant with ISO/IEC 27037:2012

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.10+ (Tested & verified on **Python 3.14.4**)
- Dependencies already installed: `fastapi`, `uvicorn`, `cryptography`, `jinja2`, `python-multipart`

### 2. Run the Application
In your terminal, execute:
```powershell
python run.py
```
This automatically starts the server at `http://127.0.0.1:8000` and opens your browser.

### 3. Share Website with Free Public Domain (₹0)
To generate an instant, secure public HTTPS URL that anyone across the globe can open:
```powershell
.\start_public_tunnel.bat
```
*(Powered by Cloudflare Tunnel - 100% Free with automated SSL).*

### 3. Run Automated Tests
```powershell
python test_system.py
```

---

## 📂 Project Architecture

```
├── backend/
│   ├── config.py             # Vault paths, encryption salts, iterations
│   ├── crypto_engine.py      # Dual hashing, AES-256-GCM, Merkle root
│   ├── storage_optimizer.py  # Deduplication, compression, vault storage
│   ├── blockchain_ledger.py  # Append-only immutable Chain of Custody
│   ├── models.py             # Pydantic data schemas
│   └── app.py                # FastAPI endpoints & certificate generator
├── static/
│   ├── css/styles.css        # Cyber-forensic dark glassmorphism UI
│   ├── js/app.js             # Real-time telemetry, charts, API client
│   └── index.html            # Single Page Forensic Web Dashboard
├── data/                     # Encrypted vault blobs & ledger (auto-generated)
├── run.py                    # One-click system launcher
├── test_system.py            # Automated test suite
└── PROJECT_DOCUMENTATION.md  # Comprehensive academic report, SRS & Viva Q&A
```

---

## 📜 Full Documentation
For the complete project report, system architecture diagrams, mathematical formulations, and examiner viva voce questions, refer to [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md).
