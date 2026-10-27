import os
import re
import uuid
import mimetypes
from werkzeug.utils import secure_filename
from app.config import Config

DANGEROUS_EXTENSIONS = {
    'exe', 'bat', 'cmd', 'sh', 'php', 'py', 'pl', 'cgi', 'jar',
    'vbs', 'msi', 'scr', 'com', 'pif', 'ps1', 'dll', 'bin'
}

MIME_TYPE_MAPPING = {
    'image': {'jpg', 'jpeg', 'png', 'webp', 'gif', 'svg'},
    'video': {'mp4', 'webm', 'mov', 'avi', 'mkv'},
    'audio': {'mp3', 'wav', 'ogg', 'm4a', 'aac'},
    'creative': {'ai', 'psd', 'eps'},
    'document': {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv', 'zip'}
}


class StorageService:
    @classmethod
    def get_storage_dir(cls):
        path = os.path.abspath(Config.STORAGE_DIR)
        os.makedirs(path, exist_ok=True)
        return path

    @classmethod
    def get_extension(cls, filename):
        if not filename or '.' not in filename:
            return ''
        return filename.rsplit('.', 1)[1].lower().strip()

    @classmethod
    def get_file_category(cls, filename, mime_type=None):
        ext = cls.get_extension(filename)
        for cat, ext_set in MIME_TYPE_MAPPING.items():
            if ext in ext_set:
                return cat
        if mime_type:
            if mime_type.startswith('image/'):
                return 'image'
            if mime_type.startswith('video/'):
                return 'video'
            if mime_type.startswith('audio/'):
                return 'audio'
        return 'document'

    @classmethod
    def validate_file(cls, filename, file_size=None, mime_type=None):
        if not filename:
            return False, "اسم الملف مطلوب"

        ext = cls.get_extension(filename)
        if not ext:
            return False, "امتداد الملف غير صالح"

        if ext in DANGEROUS_EXTENSIONS:
            return False, "نوع الملف غير مسموح به لأسباب أمنية"

        allowed = getattr(Config, 'ALLOWED_EXTENSIONS', None)
        if allowed and ext not in allowed:
            return False, f"امتداد الملف .{ext} غير مدعوم حالياً"

        max_size = getattr(Config, 'MAX_CONTENT_LENGTH', 25 * 1024 * 1024)
        if file_size and file_size > max_size:
            max_mb = max_size // (1024 * 1024)
            return False, f"حجم الملف يتجاوز الحد الأقصى المسموح ({max_mb}MB)"

        return True, ""

    @classmethod
    def generate_storage_key(cls, original_filename):
        ext = cls.get_extension(original_filename)
        clean_name = secure_filename(original_filename)
        # Strip extension from clean_name to avoid duplicating it
        base_name = clean_name.rsplit('.', 1)[0] if '.' in clean_name else clean_name
        base_name = re.sub(r'[^a-zA-Z0-9_-]', '_', base_name)[:40] or 'file'
        unique_token = uuid.uuid4().hex
        return f"{unique_token}_{base_name}.{ext}" if ext else f"{unique_token}_{base_name}"

    @classmethod
    def save_file(cls, file_storage, custom_filename=None):
        original_name = custom_filename or file_storage.filename or "attachment"
        is_valid, err_msg = cls.validate_file(original_name)
        if not is_valid:
            raise ValueError(err_msg)

        storage_key = cls.generate_storage_key(original_name)
        storage_dir = cls.get_storage_dir()
        dest_path = os.path.join(storage_dir, storage_key)

        file_storage.save(dest_path)
        file_size = os.path.getsize(dest_path)

        max_size = getattr(Config, 'MAX_CONTENT_LENGTH', 25 * 1024 * 1024)
        if file_size > max_size:
            os.remove(dest_path)
            max_mb = max_size // (1024 * 1024)
            raise ValueError(f"حجم الملف يتجاوز الحد الأقصى المسموح ({max_mb}MB)")

        mime_type = file_storage.content_type or mimetypes.guess_type(original_name)[0] or 'application/octet-stream'
        file_category = cls.get_file_category(original_name, mime_type)

        return {
            "storage_key": storage_key,
            "file_name": original_name,
            "file_size": file_size,
            "mime_type": mime_type,
            "file_type": file_category,
            "file_url": f"/api/attachments/preview/{storage_key}"
        }

    @classmethod
    def save_bytes(cls, data_bytes, filename, mime_type=None):
        is_valid, err_msg = cls.validate_file(filename, file_size=len(data_bytes))
        if not is_valid:
            raise ValueError(err_msg)

        storage_key = cls.generate_storage_key(filename)
        storage_dir = cls.get_storage_dir()
        dest_path = os.path.join(storage_dir, storage_key)

        with open(dest_path, 'wb') as f:
            f.write(data_bytes)

        file_size = len(data_bytes)
        guessed_mime = mime_type or mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        file_category = cls.get_file_category(filename, guessed_mime)

        return {
            "storage_key": storage_key,
            "file_name": filename,
            "file_size": file_size,
            "mime_type": guessed_mime,
            "file_type": file_category,
            "file_url": f"/api/attachments/preview/{storage_key}"
        }

    @classmethod
    def get_file_path(cls, storage_key):
        if not storage_key or '..' in storage_key or '/' in storage_key or '\\' in storage_key:
            return None
        storage_dir = cls.get_storage_dir()
        abs_path = os.path.abspath(os.path.join(storage_dir, storage_key))
        if not abs_path.startswith(storage_dir):
            return None
        if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            return None
        return abs_path

    @classmethod
    def delete_file(cls, storage_key):
        path = cls.get_file_path(storage_key)
        if path and os.path.exists(path):
            try:
                os.remove(path)
                return True
            except OSError:
                return False
        return False
