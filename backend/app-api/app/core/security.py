"""
Module phân quyền và xác thực người dùng (Security Dependencies).
Hỗ trợ:
- Xác thực Bearer JWT Token chuẩn theo RFC 6750.
- Cơ chế Dev Mode Mock Header (X-User-Id / dev-token) giúp đội Frontend kiểm thử ngay lập tức.
"""
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from backend.shared.database.session import get_db
from backend.shared.models import User
from backend.shared.enums import UserRole
from backend.shared.authentication import decode_access_token

# Khởi tạo Bearer security scheme (auto_error=False để hỗ trợ fallback khi dev)
security_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency lấy thông tin người dùng đang đăng nhập:
    1. Kiểm tra JWT token trong header 'Authorization: Bearer <token>'
    2. Nếu ở môi trường dev, cho phép dùng token mẫu 'dev-token-<id>' hoặc header 'X-User-Id'
    3. Nếu không truyền gì ở môi trường dev, tự động gán tài khoản Customer mẫu đầu tiên để FE test thông suốt.
    """
    user_id: Optional[int] = None

    # 1. Kiểm tra Token từ Authorization Header
    if credentials and credentials.credentials:
        token = credentials.credentials.strip()

        # Hỗ trợ token dev tiện lợi: "dev-token-4"
        if token.startswith("dev-token-"):
            try:
                user_id = int(token.replace("dev-token-", ""))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Dev token không hợp lệ (Định dạng đúng: 'dev-token-<id>').",
                    headers={"WWW-Authenticate": "Bearer"}
                )
        else:
            payload = decode_access_token(token)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token xác thực không hợp lệ hoặc đã hết hạn.",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            # sub hoặc user_id trong JWT payload
            raw_id = payload.get("sub") or payload.get("user_id")
            try:
                user_id = int(raw_id)
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Payload token chứa user_id không hợp lệ.",
                    headers={"WWW-Authenticate": "Bearer"}
                )

    # 2. Hỗ trợ Dev Mode Fallback nếu chưa đăng nhập
    if user_id is None and (settings.APP_ENV == "development" or settings.APP_DEBUG):
        # Kiểm tra custom header X-User-Id
        dev_header_id = request.headers.get("x-user-id")
        if dev_header_id and dev_header_id.isdigit():
            user_id = int(dev_header_id)
        else:
            # Fallback lấy khách hàng Customer đầu tiên trong DB
            fallback_stmt = select(User).where(User.role == UserRole.CUSTOMER).order_by(User.user_id.asc())
            fallback_user = (await db.execute(fallback_stmt)).scalars().first()
            if fallback_user:
                return fallback_user

    # 3. Nếu ở production hoặc không tìm thấy user_id
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yêu cầu xác thực tài khoản. Vui lòng cung cấp Bearer Token hợp lệ.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 4. Truy vấn người dùng từ cơ sở dữ liệu
    stmt = select(User).where(User.user_id == user_id)
    user = (await db.execute(stmt)).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Người dùng với ID {user_id} không tồn tại trên hệ thống."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản của bạn đã bị khóa hoặc ngừng hoạt động."
        )

    return user
