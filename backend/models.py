from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class LoginInitiateRequest(BaseModel):
    email: str = Field(..., description="Operator registered email")
    password: str = Field(..., description="Operator password")

class LoginVerifyOtpRequest(BaseModel):
    email: str = Field(..., description="Operator registered email")
    otp: str = Field(..., description="6-digit verification code")

class RegisterInitiateRequest(BaseModel):
    email: str = Field(..., description="New operator email")
    password: str = Field(..., description="Desired password")
    name: str = Field(..., description="Officer or analyst full name")
    role: str = Field("Forensic Investigator", description="Department role")

class RegisterVerifyOtpRequest(BaseModel):
    email: str = Field(..., description="New operator email")
    otp: str = Field(..., description="6-digit verification code")
    password: str = Field(..., description="Desired password")
    name: str = Field(..., description="Officer or analyst full name")
    role: str = Field("Forensic Investigator", description="Department role")

class CustodyTransferRequest(BaseModel):
    evidence_id: str = Field(..., description="Unique Evidence ID")
    action: str = Field(..., description="Action type")
    current_custodian: str = Field(..., description="Current authorized custodian")
    recipient: str = Field(..., description="New custodian, analyst, or court authority")
    notes: Optional[str] = Field("", description="Detailed forensic notes")

class TamperTestRequest(BaseModel):
    block_index: int = Field(..., description="Index of block to intentionally tamper with")
    malicious_action: Optional[str] = Field("UNAUTHORIZED_RECORD_ALTERATION", description="Altered payload")

class EvidenceVerificationResponse(BaseModel):
    evidence_id: str
    filename: str
    integrity_valid: bool
    stored_sha256: str
    recomputed_sha256: str
    stored_blake2b: str
    recomputed_blake2b: str
    tampered: bool

class StorageStatsResponse(BaseModel):
    total_evidence_count: int
    unique_vault_blobs: int
    deduplicated_files: int
    total_uncompressed_bytes: int
    total_vault_stored_bytes: int
    total_bytes_saved: int
    storage_reduction_percentage: float
