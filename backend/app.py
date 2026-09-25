import os
import io
import uuid
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import json
import hashlib
from backend.config import BASE_DIR, APP_TITLE, APP_VERSION, ACADEMIC_YEAR, FIREBASE_CONFIG_FILE
from backend.storage_optimizer import StorageOptimizer
from backend.blockchain_ledger import BlockchainLedger
from backend.auth import AuthManager
from backend.models import (
    CustodyTransferRequest, TamperTestRequest,
    LoginInitiateRequest, LoginVerifyOtpRequest,
    RegisterInitiateRequest, RegisterVerifyOtpRequest
)

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="Optimizing Digital Forensic Security Via Secure Storage - Final Year Project System"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

optimizer = StorageOptimizer()
ledger = BlockchainLedger()
auth_mgr = AuthManager()

# --- AUTHENTICATION & EMAIL OTP ROUTES ---

@app.get("/api/auth/demo-users")
def get_demo_users():
    """Returns list of pre-configured demo operators."""
    return auth_mgr.get_demo_users()

@app.post("/api/auth/login/initiate")
def login_initiate(payload: LoginInitiateRequest):
    """Step 1: Authenticates email/password and dispatches 6-digit OTP."""
    result = auth_mgr.initiate_login(payload.email, payload.password)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result

@app.post("/api/auth/login/verify")
def login_verify(payload: LoginVerifyOtpRequest):
    """Step 2: Validates OTP, logs access on ledger, and issues token."""
    result = auth_mgr.complete_login(payload.email, payload.otp)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Log successful MFA authentication on blockchain
    user = result["user"]
    ledger.add_block(
        case_id="AUTH_SESSION",
        evidence_id="MFA_OPERATOR_LOGIN",
        action="OPERATOR_AUTHENTICATED_MFA_OTP",
        custodian=f"{user['name']} ({user['badge']})",
        evidence_hash=user["token"][:32],
        notes=f"Email OTP 2-Factor Authentication verified for {user['email']}"
    )

    return result

@app.post("/api/auth/register/initiate")
def register_initiate(payload: RegisterInitiateRequest):
    """Step 1: Validates new operator registration and dispatches OTP."""
    result = auth_mgr.initiate_registration(payload.email, payload.password, payload.name, payload.role)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/api/auth/register/verify")
def register_verify(payload: RegisterVerifyOtpRequest):
    """Step 2: Validates registration OTP and activates account."""
    result = auth_mgr.complete_registration(
        payload.email, payload.otp, payload.password, payload.name, payload.role
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    user = result["user"]
    ledger.add_block(
        case_id="REGISTRATION",
        evidence_id="OPERATOR_ONBOARDING",
        action="NEW_OPERATOR_REGISTERED_OTP",
        custodian=f"{user['name']} ({user['badge']})",
        evidence_hash=user["id"],
        notes=f"New forensic operator registered with clearance: {user['clearance']}"
    )

    return result

# --- GOOGLE FIREBASE CLOUD INTEGRATION ROUTES ---

@app.get("/api/firebase/config")
def get_firebase_config():
    """Returns Google Firebase Client Configuration."""
    if FIREBASE_CONFIG_FILE.exists():
        try:
            with open(FIREBASE_CONFIG_FILE, "r", encoding="utf-8") as ff:
                return json.load(ff)
        except Exception:
            pass
    return {"firebase_enabled": False}

@app.post("/api/firebase/config")
async def update_firebase_config(payload: dict):
    """Updates Google Firebase project credentials."""
    try:
        with open(FIREBASE_CONFIG_FILE, "w", encoding="utf-8") as ff:
            json.dump(payload, ff, indent=2)
        return {"success": True, "message": "Firebase configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/firebase/sync-log")
async def log_firebase_sync(payload: dict):
    """Logs a Google Firebase Cloud Firestore synchronization block to the immutable ledger."""
    evidence_id = payload.get("evidence_id", "FIRESTORE_CLOUD_SYNC")
    actor = payload.get("operator", "Google Firebase Cloud Engine")
    cloud_doc_id = payload.get("firestore_doc_id", "DOC-" + uuid.uuid4().hex[:8])

    new_block = ledger.add_block(
        case_id="CLOUD_SYNC",
        evidence_id=evidence_id,
        action="FIREBASE_FIRESTORE_CLOUD_SYNC",
        custodian=actor,
        evidence_hash=hashlib.sha256(cloud_doc_id.encode()).hexdigest(),
        notes=f"Forensic artifact mirrored to Google Cloud Firestore [Doc ID: {cloud_doc_id}]"
    )
    return {"success": True, "block": new_block.to_dict()}

@app.get("/")
def read_root():
    """Serves the primary Cyber Forensic Web Dashboard."""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return HTMLResponse("<h1>Forensic Storage Engine Running</h1><p>Static UI initializing...</p>")

@app.get("/api/health")
def health_check():
    return {
        "status": "ONLINE",
        "system": APP_TITLE,
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/evidence/upload")
async def upload_evidence(
    file: UploadFile = File(...),
    case_id: str = Form("CASE-2026-001"),
    custodian: str = Form("Lead Investigator Agent"),
    classification: str = Form("Confidential"),
    notes: str = Form("Forensic image acquired from primary suspect target")
):
    """
    Forensic Evidence Acquisition & Ingestion:
    1. Reads raw artifact bytes
    2. Computes SHA-256 + BLAKE2b dual hashes
    3. Executes content-addressable deduplication check
    4. Compresses (zlib level 9) & Encrypts (AES-256-GCM)
    5. Commits tamper-proof record to Immutable Blockchain Ledger
    """
    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded evidence file is empty.")

    # Unique Evidence Tracking ID
    evidence_id = f"EV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    # Optimize and store in vault
    record = optimizer.optimize_and_store(
        evidence_id=evidence_id,
        filename=file.filename or "unnamed_artifact.bin",
        raw_data=raw_bytes,
        case_id=case_id,
        custodian=custodian,
        classification=classification
    )

    # Append acquisition to Blockchain Chain of Custody
    block_action = "SEIZED_AND_VAULT_STORED" if not record["is_duplicate"] else "SEIZED_AND_DEDUPLICATED"
    audit_notes = f"{notes} | Storage: {record['status']} | Ratio: {record['compression_ratio_pct']}%"
    
    new_block = ledger.add_block(
        case_id=case_id,
        evidence_id=evidence_id,
        action=block_action,
        custodian=custodian,
        evidence_hash=record["content_hash"],
        notes=audit_notes
    )

    return {
        "success": True,
        "evidence": record,
        "blockchain_block": new_block.to_dict()
    }

@app.get("/api/evidence/list")
def list_evidence():
    """Returns all forensic evidence catalog records."""
    records = optimizer.get_all_metadata()
    return list(records.values())

@app.get("/api/evidence/{evidence_id}")
def get_evidence_details(evidence_id: str):
    """Returns specific evidence metadata alongside its complete Chain of Custody history."""
    records = optimizer.get_all_metadata()
    if evidence_id not in records:
        raise HTTPException(status_code=404, detail="Evidence not found.")
    
    history = ledger.get_evidence_history(evidence_id)
    return {
        "evidence": records[evidence_id],
        "chain_of_custody": history
    }

@app.post("/api/evidence/transfer")
def transfer_custody(payload: CustodyTransferRequest):
    """
    Transfers custody of an evidence artifact to another investigator, analyst, or court.
    Permanently recorded in the blockchain ledger.
    """
    records = optimizer.get_all_metadata()
    if payload.evidence_id not in records:
        raise HTTPException(status_code=404, detail="Evidence ID not found.")

    evidence_hash = records[payload.evidence_id]["content_hash"]
    case_id = records[payload.evidence_id]["case_id"]

    new_block = ledger.add_block(
        case_id=case_id,
        evidence_id=payload.evidence_id,
        action=payload.action,
        custodian=payload.current_custodian,
        recipient=payload.recipient,
        evidence_hash=evidence_hash,
        notes=payload.notes or f"Custody transferred from {payload.current_custodian} to {payload.recipient}"
    )

    return {
        "success": True,
        "message": f"Custody successfully transferred to {payload.recipient}",
        "block": new_block.to_dict()
    }

@app.get("/api/evidence/verify/{evidence_id}")
def verify_evidence(evidence_id: str):
    """
    Performs full zero-trust forensic verification:
    1. Loads vault file
    2. Verifies AES-256-GCM authentication tag
    3. Decompresses and re-computes dual hashes (SHA-256 + BLAKE2b)
    4. Compares against ledger recorded hashes
    """
    _, report = optimizer.retrieve_and_verify(evidence_id)
    if "error" in report and "tampered" not in report:
        raise HTTPException(status_code=404, detail=report["error"])

    # Cross-reference with blockchain
    blocks = [b for b in ledger.chain if b.evidence_id == evidence_id]
    ledger_hash_matches = any(b.evidence_hash == report.get("stored_sha256") for b in blocks)
    report["ledger_hash_matches"] = ledger_hash_matches

    # Auto-log this verification check on the blockchain
    if report.get("integrity_valid"):
        ledger.add_block(
            case_id="VERIFY_AUDIT",
            evidence_id=evidence_id,
            action="INTEGRITY_AUDIT_PASSED",
            custodian="Automated Forensic Verifier",
            evidence_hash=report["stored_sha256"],
            notes="Cryptographic dual-digest and AES-GCM tag verification succeeded."
        )

    return report

@app.get("/api/evidence/download/{evidence_id}")
def download_evidence(evidence_id: str, requestor: str = "Authorized Forensic Analyst"):
    """
    Decrypts artifact on-the-fly and serves as downloadable stream.
    Automatically logs an ACCESS/CHECKOUT audit event in the blockchain.
    """
    raw_bytes, report = optimizer.retrieve_and_verify(evidence_id)
    if raw_bytes is None:
        raise HTTPException(status_code=400, detail=report.get("error", "Failed to retrieve evidence."))

    filename = report.get("filename", "decrypted_evidence.bin")

    # Record access block
    ledger.add_block(
        case_id="CHECKOUT_LOG",
        evidence_id=evidence_id,
        action="EVIDENCE_EXPORT_AND_CHECKOUT",
        custodian=requestor,
        evidence_hash=report["stored_sha256"],
        notes=f"Authorized export and decryption by {requestor}"
    )

    return StreamingResponse(
        io.BytesIO(raw_bytes),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.get("/api/ledger/blocks")
def get_ledger_blocks():
    """Returns the complete sequence of Chain of Custody blocks."""
    return ledger.get_all_blocks()

@app.get("/api/ledger/validate")
def validate_ledger():
    """Scans and audits the entire blockchain ledger and Merkle tree."""
    return ledger.validate_chain()

@app.post("/api/ledger/tamper")
def simulate_tamper(payload: TamperTestRequest):
    """Demo endpoint: Intentionally corrupts a block to demonstrate detection."""
    result = ledger.simulate_tampering(payload.block_index, payload.malicious_action)
    return result

@app.post("/api/ledger/repair")
def repair_ledger():
    """Repairs the blockchain chain hashes after a tamper demonstration."""
    return ledger.repair_chain_recompute()

@app.get("/api/stats")
def get_storage_stats():
    """Returns real-time storage optimization and security metrics."""
    stats = optimizer.get_optimization_stats()
    ledger_status = ledger.validate_chain()
    stats["ledger_healthy"] = ledger_status.get("is_valid", False)
    stats["total_blockchain_blocks"] = len(ledger.chain)
    return stats

@app.get("/api/certificate/{evidence_id}", response_class=HTMLResponse)
def generate_court_certificate(evidence_id: str):
    """
    Generates a court-admissible Digital Evidence Chain of Custody Certificate
    formatted for legal proceedings, judicial submission, or viva examination.
    """
    records = optimizer.get_all_metadata()
    if evidence_id not in records:
        raise HTTPException(status_code=404, detail="Evidence not found.")

    meta = records[evidence_id]
    history = ledger.get_evidence_history(evidence_id)
    validation = optimizer.retrieve_and_verify(evidence_id)
    integrity_status = "VERIFIED & UNCOMPROMISED" if validation[1].get("integrity_valid") else "TAMPER WARNING"

    events_html = "".join([
        f"""<tr>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold;">Block #{b['index']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{b['timestamp']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; color: #0d47a1; font-weight: bold;">{b['action']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{b['custodian']} {f"&rarr; {b['recipient']}" if b.get('recipient') else ""}</td>
            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-size: 11px; font-family: monospace;">{b['block_hash'][:16]}...</td>
        </tr>"""
        for b in history
    ])

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Court-Admissible Evidence Certificate - {evidence_id}</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 40px; color: #111; }}
        .header {{ text-align: center; border-bottom: 3px double #000; padding-bottom: 20px; }}
        .watermark {{ font-size: 14px; text-transform: uppercase; letter-spacing: 2px; color: #555; }}
        h1 {{ margin: 5px 0; font-size: 24px; text-transform: uppercase; }}
        .badge {{ display: inline-block; padding: 4px 12px; background: #e8f5e9; color: #2e7d32; font-weight: bold; border: 1px solid #2e7d32; border-radius: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }}
        th {{ background-color: #f2f2f2; text-align: left; padding: 10px; border-bottom: 2px solid #aaa; }}
        .hash-box {{ font-family: monospace; font-size: 12px; background: #f8f9fa; padding: 8px; border: 1px solid #ccc; word-break: break-all; margin-top: 4px; }}
        .print-btn {{ margin-bottom: 20px; padding: 10px 20px; background: #007bff; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }}
        @media print {{ .print-btn {{ display: none; }} }}
    </style>
</head>
<body>
    <button class="print-btn" onclick="window.print()">🖨️ Print Official Certificate (PDF / Court Admissible)</button>
    <div class="header">
        <div class="watermark">Digital Forensic Evidence Laboratory &bull; Court Compliance Registry</div>
        <h1>CERTIFICATE OF DIGITAL EVIDENCE INTEGRITY</h1>
        <p>In accordance with ISO/IEC 27037:2012 Guidelines for Identification, Collection, Acquisition and Preservation of Digital Evidence</p>
    </div>

    <div style="margin-top: 25px; display: flex; justify-content: space-between;">
        <div>
            <p><strong>Evidence Identification:</strong> {evidence_id}</p>
            <p><strong>Original File Name:</strong> {meta['filename']}</p>
            <p><strong>Associated Case Number:</strong> {meta['case_id']}</p>
            <p><strong>Classification:</strong> {meta['classification']}</p>
        </div>
        <div>
            <p><strong>Integrity Status:</strong> <span class="badge">{integrity_status}</span></p>
            <p><strong>Initial Custodian:</strong> {meta['custodian']}</p>
            <p><strong>Original File Size:</strong> {meta['raw_size_bytes']} bytes</p>
            <p><strong>Optimized Vault Size:</strong> {meta['vault_size_bytes']} bytes ({meta['compression_ratio_pct']}% reduction)</p>
        </div>
    </div>

    <h3>Cryptographic Integrity Fingerprints</h3>
    <div><strong>SHA-256 Digest:</strong><div class="hash-box">{meta['content_hash']}</div></div>
    <div style="margin-top: 8px;"><strong>BLAKE2b Digest:</strong><div class="hash-box">{meta['blake2b_hash']}</div></div>
    <div style="margin-top: 8px;"><strong>Physical Vault Blob Reference:</strong><div class="hash-box">{meta['vault_file']} (AES-256-GCM Encrypted)</div></div>

    <h3 style="margin-top: 30px;">Immutable Blockchain Chain of Custody Audit Trail</h3>
    <table>
        <thead>
            <tr>
                <th>Block #</th>
                <th>Timestamp (UTC)</th>
                <th>Custody Action</th>
                <th>Authorized Actor</th>
                <th>Block Cryptographic Signature</th>
            </tr>
        </thead>
        <tbody>
            {events_html}
        </tbody>
    </table>

    <div style="margin-top: 40px; border-top: 1px solid #aaa; padding-top: 20px;">
        <p><strong>Forensic Examiner Certification:</strong></p>
        <p>I hereby certify that the digital evidence listed above has been securely acquired, processed through lossless cryptographic deduplication and AES-256-GCM authenticated encryption, and committed to an append-only cryptographic blockchain ledger. The integrity has been mathematically validated and remains free from unauthorized tampering.</p>
        <br>
        <div style="display: flex; justify-content: space-between; margin-top: 20px;">
            <div>___________________________________<br>Lead Digital Forensic Investigator</div>
            <div>___________________________________<br>Evidence Custodian / Lab Director</div>
            <div>___________________________________<br>Date of Judicial Submission</div>
        </div>
    </div>
</body>
</html>"""
    return HTMLContent if False else HTMLResponse(content=html_content)
