"""Object storage integration package."""
from .service import storage_service
from .validator import validate_image_upload

__all__ = ["storage_service", "validate_image_upload"]
