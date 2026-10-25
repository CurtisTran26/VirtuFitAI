"""
Enum trạng thái yêu cầu thiết kế riêng (Custom Design Request).
Luồng: Customer gửi → AI tạo concept → Designer đánh giá → báo giá → Customer duyệt.
"""
import enum


class DesignRequestStatus(str, enum.Enum):
    """Trạng thái luồng thiết kế riêng."""
    SUBMITTED = "submitted"                    # Customer vừa gửi yêu cầu
    AI_GENERATING = "ai_generating"            # AI đang tạo concept
    AI_COMPLETED = "ai_completed"              # AI đã trả kết quả
    AI_FAILED = "ai_failed"                    # AI xử lý thất bại
    REVIEWING = "reviewing"                    # Designer đang đánh giá khả thi
    REVISION_REQUESTED = "revision_requested"  # Designer yêu cầu chỉnh sửa/bổ sung
    QUOTED = "quoted"                          # Designer đã báo giá
    APPROVED = "approved"                      # Customer đã duyệt mẫu + giá
    REJECTED = "rejected"                      # Customer từ chối
    IN_PRODUCTION = "in_production"            # Đang sản xuất
    COMPLETED = "completed"                    # Hoàn thành, chuyển qua đơn hàng
