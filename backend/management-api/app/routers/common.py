from __future__ import annotations

import hashlib
import json
import os
import secrets
from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from shared_platform import get_db, current_user, require_roles, verify_password, hash_password, issue_session, now
from app.schemas.management import *

v1 = "/api/v1"
Admin = Depends(require_roles("admin"))
CatalogEditor = Depends(require_roles("admin", "warehouse_staff"))
Warehouse = Depends(require_roles("admin", "warehouse_staff"))
