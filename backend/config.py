import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VAULT_DIR = DATA_DIR / "vault"
LEDGER_FILE = DATA_DIR / "ledger.json"
METADATA_FILE = DATA_DIR / "evidence_metadata.json"
KEYS_FILE = DATA_DIR / "vault_keys.json"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
VAULT_DIR.mkdir(parents=True, exist_ok=True)

# Cryptographic Salt & Master Config
DEFAULT_MASTER_KEY = os.getenv("FORENSIC_MASTER_KEY", "CyberForensics-SecureVault-2026-FinalYear")
PBKDF2_ITERATIONS = 100_000
HASH_ALGORITHMS = ["SHA-256", "BLAKE2b"]
GCM_TAG_SIZE = 16
GCM_IV_SIZE = 12

# Application Metadata
APP_TITLE = "Optimizing Digital Forensic Security Via Secure Storage"
APP_VERSION = "2.0.0"
ACADEMIC_YEAR = "2025-2026"

# Email SMTP Settings (Loads from email_config.json or environment variables)
EMAIL_CONFIG_FILE = BASE_DIR / "email_config.json"
smtp_cfg = {}
if EMAIL_CONFIG_FILE.exists():
    try:
        import json
        with open(EMAIL_CONFIG_FILE, "r", encoding="utf-8") as ef:
            smtp_cfg = json.load(ef)
    except Exception:
        pass

SMTP_ENABLED = os.getenv("SMTP_ENABLED", str(smtp_cfg.get("smtp_enabled", "false"))).lower() == "true"
SMTP_HOST = os.getenv("SMTP_HOST", smtp_cfg.get("smtp_host", "smtp.gmail.com"))
SMTP_PORT = int(os.getenv("SMTP_PORT", smtp_cfg.get("smtp_port", 587)))
SMTP_USER = os.getenv("SMTP_USER", smtp_cfg.get("smtp_email", ""))
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", smtp_cfg.get("smtp_app_password", ""))
SMTP_FROM = os.getenv("SMTP_FROM", smtp_cfg.get("smtp_email", "forensics-lab@court.gov"))

# Firebase Configuration File
FIREBASE_CONFIG_FILE = BASE_DIR / "firebase_config.json"

