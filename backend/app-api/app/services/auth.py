from __future__ import annotations

import hashlib
import os
import secrets
from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from shared_platform import now


def create_otp(db: Session, phone: str, purpose: str):
    recent = db.execute(text("SELECT count(*) FROM otp_challenges WHERE phone=:p AND created_at > now()-interval '1 hour'"), {"p": phone}).scalar_one()
    if recent >= 5:
        raise HTTPException(429, detail={"code": "OTP_RATE_LIMIT", "message": "Too many codes requested"})
    code = f"{secrets.randbelow(1_000_000):06d}"
    db.execute(text("INSERT INTO otp_challenges(phone,purpose,code_hash,expires_at) VALUES(:p,:purpose,:hash,:exp)"),
               {"p": phone, "purpose": purpose, "hash": hashlib.sha256(code.encode()).hexdigest(), "exp": now() + timedelta(minutes=5)})
    db.commit()
    result = {"message": "OTP request accepted"}
    if os.getenv("OTP_DEBUG", "false").lower() == "true":
        result["debug_code"] = code
    return result


def consume_otp(db: Session, phone: str, purpose: str, code: str):
    row = db.execute(text("SELECT id,code_hash,attempts FROM otp_challenges WHERE phone=:p AND purpose=:purpose AND consumed_at IS NULL AND expires_at>now() ORDER BY created_at DESC LIMIT 1 FOR UPDATE"),
                     {"p": phone, "purpose": purpose}).mappings().first()
    if not row or row["attempts"] >= 5 or row["code_hash"] != hashlib.sha256(code.encode()).hexdigest():
        if row:
            db.execute(text("UPDATE otp_challenges SET attempts=attempts+1 WHERE id=:id"), {"id": row["id"]})
        db.commit()
        raise HTTPException(400, detail={"code": "OTP_INVALID", "message": "OTP is invalid or expired"})
    db.execute(text("UPDATE otp_challenges SET consumed_at=now() WHERE id=:id"), {"id": row["id"]})
