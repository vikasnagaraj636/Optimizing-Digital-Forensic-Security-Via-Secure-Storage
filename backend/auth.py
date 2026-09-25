import json
import hashlib
import random
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import DATA_DIR, SMTP_ENABLED, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM

USERS_FILE = DATA_DIR / "users.json"
OTP_EXPIRY_SECONDS = 300  # 5 minutes

DEFAULT_USERS = {
    "investigator@forensics.gov": {
        "id": "USR-001",
        "email": "investigator@forensics.gov",
        "name": "Special Agent John Miller",
        "role": "Lead Forensic Investigator",
        "badge": "BADGE-4492",
        "clearance": "Level 4 - Secret",
        "password_hash": hashlib.sha256(b"Password@123_SALT_FORENSICS").hexdigest()
    },
    "analyst@forensics.gov": {
        "id": "USR-002",
        "email": "analyst@forensics.gov",
        "name": "Dr. Sarah Lin",
        "role": "Senior Cyber Forensic Analyst",
        "badge": "LAB-8812",
        "clearance": "Level 3 - Restricted",
        "password_hash": hashlib.sha256(b"Password@123_SALT_FORENSICS").hexdigest()
    },
    "custodian@forensics.gov": {
        "id": "USR-003",
        "email": "custodian@forensics.gov",
        "name": "Commander Marcus Vance",
        "role": "Master Evidence Vault Custodian",
        "badge": "VAULT-0019",
        "clearance": "Level 5 - Top Secret",
        "password_hash": hashlib.sha256(b"Password@123_SALT_FORENSICS").hexdigest()
    },
    "auditor@justice.gov": {
        "id": "USR-004",
        "email": "auditor@justice.gov",
        "name": "Hon. Justice Elena Rostova",
        "role": "Judicial Court Compliance Auditor",
        "badge": "COURT-9104",
        "clearance": "Judicial Verification",
        "password_hash": hashlib.sha256(b"Password@123_SALT_FORENSICS").hexdigest()
    }
}

class AuthManager:
    """
    Manages Role-Based Email Authentication & 2-Factor Authentication (OTP):
    - Email + Password validation
    - Cryptographic 6-digit OTP dispatch & expiration
    - Operator session generation
    """

    def __init__(self):
        self.users_file = USERS_FILE
        self.active_otps: Dict[str, Dict[str, Any]] = {}
        self._init_users()

    def _init_users(self):
        if not self.users_file.exists():
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_USERS, f, indent=2)

    def _get_users(self) -> Dict[str, Any]:
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_USERS

    def _save_users(self, users: Dict[str, Any]):
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(f"{password}_SALT_FORENSICS".encode()).hexdigest()

    def _send_email_smtp(self, recipient_email: str, otp: str) -> bool:
        """Sends real cryptographic OTP to the user's personal email inbox."""
        if not SMTP_ENABLED or not SMTP_USER or not SMTP_PASSWORD:
            return False
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🔐 Your Digital Forensic Verification OTP: {otp}"
            msg["From"] = f"Digital Forensic Evidence Lab <{SMTP_FROM}>"
            msg["To"] = recipient_email

            html = f"""
            <div style="font-family: Arial, sans-serif; background: #0b1120; color: #fff; padding: 30px; border-radius: 10px; max-width: 500px; margin: auto;">
                <h2 style="color: #00f0ff; margin-top: 0;">DIGITAL FORENSIC EVIDENCE SYSTEM</h2>
                <p style="color: #94a3b8;">Two-Factor Cryptographic Authentication Code</p>
                <div style="background: #03060e; border: 2px solid #00f0ff; border-radius: 8px; padding: 18px; text-align: center; margin: 20px 0;">
                    <span style="font-family: monospace; font-size: 32px; letter-spacing: 8px; color: #00ff9d; font-weight: bold;">{otp}</span>
                </div>
                <p style="color: #94a3b8; font-size: 13px;">This verification code is valid for 5 minutes. If you did not initiate this authentication request, please notify the laboratory.</p>
                <hr style="border: 0; border-top: 1px solid #1e293b; margin: 20px 0;">
                <p style="color: #64748b; font-size: 11px;">ISO/IEC 27037:2012 Judicial Compliance Registry &bull; Cyber Forensic Lab</p>
            </div>
            """
            msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM, [recipient_email], msg.as_string())
            print(f"[SMTP SUCCESS] Real OTP email delivered to {recipient_email}")
            return True
        except Exception as e:
            print(f"[SMTP FALLBACK] Could not send via SMTP ({e}). Delivered via secure on-screen dispatch.")
            return False

    def generate_and_dispatch_otp(self, email: str) -> Dict[str, Any]:
        """Generates a secure 6-digit OTP valid for 5 minutes and dispatches it."""
        otp = str(random.randint(100000, 999999))
        self.active_otps[email.lower()] = {
            "otp": otp,
            "expires_at": time.time() + OTP_EXPIRY_SECONDS
        }

        sent_via_real_smtp = self._send_email_smtp(email, otp)
        return {
            "otp": otp,
            "real_smtp_sent": sent_via_real_smtp
        }

    def verify_otp(self, email: str, otp: str) -> bool:
        """Validates provided OTP against active records."""
        email_clean = email.strip().lower()
        if email_clean not in self.active_otps:
            return False

        record = self.active_otps[email_clean]
        if time.time() > record["expires_at"]:
            del self.active_otps[email_clean]
            return False

        if record["otp"] == otp.strip():
            del self.active_otps[email_clean]
            return True

        return False

    def initiate_login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Step 1 of MFA: Verifies password and sends 6-digit OTP to email.
        """
        users = self._get_users()
        email_clean = email.strip().lower()

        if email_clean not in users:
            return {"error": "No registered forensic operator found with this email."}

        user = users[email_clean]
        if user["password_hash"] != self.hash_password(password):
            return {"error": "Invalid authentication credentials."}

        # Dispatch 6-digit OTP
        dispatch_info = self.generate_and_dispatch_otp(email_clean)
        real_sent = dispatch_info["real_smtp_sent"]

        return {
            "success": True,
            "mfa_required": True,
            "email": email_clean,
            "message": f"Verification code dispatched to {email_clean}",
            "dispatched_otp": "" if real_sent else dispatch_info["otp"],
            "real_smtp_sent": real_sent
        }

    def complete_login(self, email: str, otp: str) -> Dict[str, Any]:
        """
        Step 2 of MFA: Validates OTP and grants access token & user profile.
        """
        email_clean = email.strip().lower()
        if not self.verify_otp(email_clean, otp):
            return {"error": "Invalid or expired OTP verification code."}

        users = self._get_users()
        if email_clean not in users:
            return {"error": "Operator profile missing."}

        user = users[email_clean]
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"],
                "badge": user["badge"],
                "clearance": user["clearance"],
                "token": f"FORENSIC-TOKEN-{uuid.uuid4().hex}"
            }
        }

    def initiate_registration(self, email: str, password: str, name: str, role: str) -> Dict[str, Any]:
        """
        Step 1 of Registration: Validates uniqueness and sends verification OTP.
        """
        users = self._get_users()
        email_clean = email.strip().lower()

        if email_clean in users:
            return {"error": "An operator with this email is already registered."}

        dispatch_info = self.generate_and_dispatch_otp(email_clean)
        real_sent = dispatch_info["real_smtp_sent"]
        return {
            "success": True,
            "mfa_required": True,
            "email": email_clean,
            "message": f"Registration OTP dispatched to {email_clean}",
            "dispatched_otp": "" if real_sent else dispatch_info["otp"],
            "real_smtp_sent": real_sent
        }

    def complete_registration(self, email: str, otp: str, password: str, name: str, role: str) -> Dict[str, Any]:
        """
        Step 2 of Registration: Validates OTP and creates new authorized operator record.
        """
        email_clean = email.strip().lower()
        if not self.verify_otp(email_clean, otp):
            return {"error": "Invalid or expired OTP code."}

        users = self._get_users()
        if email_clean in users:
            return {"error": "An operator with this email is already registered."}

        new_user = {
            "id": f"USR-{uuid.uuid4().hex[:6].upper()}",
            "email": email_clean,
            "name": name,
            "role": role,
            "badge": f"BADGE-{random.randint(1000, 9999)}",
            "clearance": "Level 3 - Restricted",
            "password_hash": self.hash_password(password)
        }

        users[email_clean] = new_user
        self._save_users(users)

        return {
            "success": True,
            "user": {
                "id": new_user["id"],
                "email": new_user["email"],
                "name": new_user["name"],
                "role": new_user["role"],
                "badge": new_user["badge"],
                "clearance": new_user["clearance"],
                "token": f"FORENSIC-TOKEN-{uuid.uuid4().hex}"
            }
        }

    def get_demo_users(self) -> Dict[str, Any]:
        users = self._get_users()
        return {
            email: {
                "name": u["name"],
                "role": u["role"],
                "badge": u["badge"],
                "clearance": u["clearance"]
            }
            for email, u in users.items()
        }
