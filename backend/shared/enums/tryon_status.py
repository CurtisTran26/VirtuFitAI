"""
Enum trạng thái tác vụ AI Virtual Try-On.
"""
import enum


class TryOnJobStatus(str, enum.Enum):
    """Trạng thái xử lý thử đồ AI."""
    PENDING = "pending"        # Đã tạo, chờ xử lý
    PROCESSING = "processing"  # AI đang xử lý ảnh
    COMPLETED = "completed"    # Thành công, có kết quả
    FAILED = "failed"          # Xử lý thất bại
