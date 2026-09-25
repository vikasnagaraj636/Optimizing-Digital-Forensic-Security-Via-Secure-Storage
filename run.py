import os
import sys
import time
import webbrowser
import threading
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

def print_banner():
    banner = r"""
================================================================================
  OPTIMIZING DIGITAL FORENSIC SECURITY VIA SECURE STORAGE
  Final Year Academic Project & Demonstration System
  Academic Year: 2025 - 2026
================================================================================
  [OK] Dual Hashing: SHA-256 + BLAKE2b (Collision-Resistant Integrity)
  [OK] Authenticated Vault: AES-256-GCM Zero-Knowledge Encryption
  [OK] Storage Optimization: Content-Addressable Deduplication & Zlib Deflate
  [OK] Chain of Custody: Append-Only Cryptographic Merkle Blockchain Ledger
  [OK] Legal Admissibility: ISO/IEC 27037 Compliant Certificates
================================================================================
"""
    print(banner)

def open_browser_delayed(url: str, delay_seconds: float = 1.5):
    time.sleep(delay_seconds)
    print(f"[*] Launching Cyber Forensic Dashboard: {url}")
    webbrowser.open(url)

def main():
    print_banner()

    # Pre-create data directories
    data_dir = BASE_DIR / "data"
    vault_dir = data_dir / "vault"
    data_dir.mkdir(parents=True, exist_ok=True)
    vault_dir.mkdir(parents=True, exist_ok=True)

    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"

    # Kill any stale python processes on port 8000
    try:
        import subprocess
        subprocess.run(
            'powershell -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"',
            shell=True
        )
    except Exception:
        pass

    # Launch browser in a background thread
    threading.Thread(target=open_browser_delayed, args=(url,), daemon=True).start()

    print(f"[*] Starting Forensic Application Server on {url} ...")
    print(f"[*] Press CTRL+C to stop the server at any time.\n")

    try:
        import uvicorn
        uvicorn.run("backend.app:app", host=host, port=port, log_level="info", reload=True)
    except KeyboardInterrupt:
        print("\n[!] Forensic Storage Server stopped gracefully.")
    except Exception as e:
        print(f"\n[X] Failed to launch server: {e}")

if __name__ == "__main__":
    main()
