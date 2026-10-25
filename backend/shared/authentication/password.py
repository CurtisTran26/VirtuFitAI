"""
Tiện ích mã hóa và xác thực mật khẩu sử dụng bcrypt.
"""
from passlib.context import CryptContext

# Cấu hình CryptContext sử dụng bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu nhập vào có khớp với mật khẩu đã mã hóa hay không."""
    if not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Mã hóa mật khẩu bằng thuật toán bcrypt."""
    return pwd_context.hash(password)
