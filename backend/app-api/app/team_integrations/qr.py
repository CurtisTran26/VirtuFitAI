"""PNG generation reused from An QRService 8079668; resolver adapted to UUID/SKU."""
import io
import re
from uuid import UUID
import qrcode
from fastapi import HTTPException
from sqlalchemy import text


class QRService:
    def generate_qr_image_bytes(self, payload):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()

    def resolve_id(self, db, content):
        value = content.strip()
        for prefix in ('VFIT:', 'virtufit://products/', 'virtufit://product/'):
            if value.startswith(prefix):
                value = value[len(prefix):].rstrip('/')
                break
        try:
            return UUID(value)
        except ValueError:
            if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', value):
                raise HTTPException(400, detail={'code':'QR_INVALID','message':'Mã QR không thuộc định dạng VirtuFitAI.'})
            uid = db.execute(text('SELECT id FROM products WHERE sku=:s'), {'s':value}).scalar()
            if not uid:
                raise HTTPException(404, detail={'code':'PRODUCT_NOT_FOUND','message':'Không tìm thấy SKU. QR ID số nguyên của database An cần được tạo lại theo UUID/SKU.'})
            return uid


qr_service = QRService()
