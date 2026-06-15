import hashlib
import re

def _is_md5_hash(value):
    """Kiểm tra xem giá trị đã là MD5 hash (32 ký tự hex) chưa."""
    if not value or len(value) != 32:
        return False
    return bool(re.match(r'^[a-fA-F0-9]{32}$', value))


def _md5_double_hash(plain_text):
    """Hash password theo chuẩn PHP cũ: md5(md5(password))."""
    first = hashlib.md5(plain_text.encode('utf-8')).hexdigest()
    return hashlib.md5(first.encode('utf-8')).hexdigest()
