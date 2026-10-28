"""Provision the first admin interactively through environment variables."""
import os
import sys

from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend/shared")))
from shared_platform import SessionLocal, hash_password

phone=os.environ.get("VIRTUFIT_ADMIN_PHONE", "")
name=os.environ.get("VIRTUFIT_ADMIN_NAME", "")
password=os.environ.get("VIRTUFIT_ADMIN_PASSWORD", "")
if not phone or not name or len(password)<16:
    raise SystemExit("Set VIRTUFIT_ADMIN_PHONE, VIRTUFIT_ADMIN_NAME and a VIRTUFIT_ADMIN_PASSWORD of at least 16 characters.")

with SessionLocal.begin() as db:
    if db.execute(text("SELECT 1 FROM users WHERE phone=:phone"), {"phone":phone}).first():
        raise SystemExit("That phone already belongs to an account; use the admin API to manage it.")
    db.execute(text("INSERT INTO users(phone,full_name,password_hash,role_id,phone_verified_at) SELECT :phone,:name,:hash,id,now() FROM roles WHERE name='admin'"),
               {"phone":phone,"name":name,"hash":hash_password(password)})
print("Initial admin created. Remove the password from the environment after this command.")
