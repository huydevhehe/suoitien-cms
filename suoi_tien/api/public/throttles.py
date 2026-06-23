from rest_framework.throttling import AnonRateThrottle


class PublicWriteThrottle(AnonRateThrottle):
    """
    Giới hạn riêng cho các API ghi dữ liệu công khai (đặt vé, đặt món, liên hệ,
    bình luận) để chống spam, tách biệt với giới hạn đọc dữ liệu thông thường.
    Tốc độ khai báo tại REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['public_write'].
    """
    scope = 'public_write'


class PublicAuthThrottle(AnonRateThrottle):
    """
    Giới hạn chặt hơn cho đăng ký/đăng nhập khách hàng để chống dò mật khẩu
    (brute-force). Tốc độ khai báo tại DEFAULT_THROTTLE_RATES['public_auth'].
    """
    scope = 'public_auth'
