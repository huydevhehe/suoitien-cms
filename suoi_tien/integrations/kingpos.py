"""
Client gọi hệ thống phát hành vé thật KingPOS (bv.suoitien.vn:5634).
Xem PHP gốc: halink-includes/libraries/functions.php (api_st_*) để đối chiếu logic.

Đây mới là bước ĐỌC dữ liệu (lấy access token + danh sách combo) phục vụ ô chọn
"Mã KingPOS" trong form Sản phẩm. Các bước GHI dữ liệu thật (Booking, BookingConfirm...)
chưa được triển khai ở đây - cần làm riêng khi có xác nhận từ Suối Tiên.
"""
import requests
from django.conf import settings
from django.core.cache import cache

TOKEN_CACHE_KEY = 'kingpos_access_token'
TOKEN_CACHE_TTL = 12 * 3600  # 12h, khớp cách bản PHP cũ cache token
COMBO_CACHE_TTL = 10 * 60    # 10 phút, tránh gọi KingPOS liên tục mỗi lần mở form sản phẩm
REQUEST_TIMEOUT = 8


def get_access_token(force_refresh=False):
    """Lấy Bearer token, cache lại để không đăng nhập lại mỗi request. Trả None nếu lỗi."""
    if not force_refresh:
        cached = cache.get(TOKEN_CACHE_KEY)
        if cached:
            return cached

    try:
        resp = requests.post(
            f'{settings.KINGPOS_BASE_URL}/v1/AccessToken',
            json={'username': settings.KINGPOS_USERNAME, 'password': settings.KINGPOS_PASSWORD},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        token = resp.json().get('accesstoken')
    except (requests.RequestException, ValueError):
        return None

    if token:
        cache.set(TOKEN_CACHE_KEY, token, TOKEN_CACHE_TTL)
    return token


def get_combo_list(id_server=None, force_refresh=False):
    """
    Trả danh sách combo thật từ KingPOS, đã làm phẳng (bỏ cấu trúc nhóm):
    [{'id': '6797', 'name': 'VÉ CỔNG BIỂN KỲ QUAN - NGƯỜI LỚN', 'price': '180000', 'group': 'COMBO CÔNG VIÊN'}, ...]
    Trả [] nếu KingPOS lỗi/không phản hồi - KHÔNG raise exception để không sập trang admin.
    """
    id_server = id_server or settings.KINGPOS_ID_SERVER
    cache_key = f'kingpos_combo_list_{id_server}'
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    token = get_access_token()
    if not token:
        return []

    try:
        resp = requests.post(
            f'{settings.KINGPOS_BASE_URL}/v1/combo',
            json={'id_Server': str(id_server)},
            headers={'Authorization': f'Bearer {token}'},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        groups = resp.json() or []
    except (requests.RequestException, ValueError):
        return []

    combos = []
    for group in groups:
        group_name = group.get('vn_name_group') or group.get('name_group') or ''
        for c in group.get('combo', []) or []:
            combos.append({
                'id': str(c.get('id', '')),
                'name': c.get('vn_name') or c.get('name') or '',
                'name_en': c.get('en_name') or '',
                'price': c.get('price', ''),
                'group': group_name,
                'image': c.get('image', ''),
                'description': c.get('vn_description') or c.get('description') or '',
                'description_en': c.get('en_description') or '',
            })

    cache.set(cache_key, combos, COMBO_CACHE_TTL)
    return combos


def find_combo_by_id(combo_id, id_server=None):
    """Tìm 1 combo theo id trong danh sách đã cache - dùng để hiển thị tên khi load form sửa."""
    if not combo_id:
        return None
    for c in get_combo_list(id_server):
        if c['id'] == str(combo_id):
            return c
    return None
