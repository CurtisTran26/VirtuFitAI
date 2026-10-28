"""
Enum vai trò người dùng trong hệ thống.
"""
import enum


class UserRole(str, enum.Enum):
    """5 vai trò theo quy định nghiệp vụ."""
    CUSTOMER = "customer"
    SALES_STAFF = "sales_staff"
    WAREHOUSE_STAFF = "warehouse_staff"
    DESIGNER = "designer"
    ADMIN = "admin"
