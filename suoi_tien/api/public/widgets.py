"""
Đọc dữ liệu Widget (Quản lý Widgets kéo thả) và gói lại thành JSON cho FE.
Chỉ phục vụ các vị trí (sidebar) thật sự được theme đọc tới — đã rà soát trực
tiếp source PHP gốc để xác nhận, xem `suoi_tien/views/widgets_config.py`.
"""
import json

from django.db.models import Q

from suoi_tien.models import HalinkMeta, HalinkMenu, HalinkPost
from suoi_tien.utils import build_media_url, clean_lang
from suoi_tien.views.widgets_config import AVAILABLE_WIDGETS
from .menu_tree import build_menu_tree
from .serializers import PostSummarySerializer

IMAGE_SUBFOLDER = 'hinhanh'

# 11 vị trí thật sự được theme đọc tới (đã grep source PHP để xác nhận).
# "Banner header" (halink_header_wg) bị loại vì không có chỗ nào gọi tới.
VALID_POSITIONS = {
    'halink_home_wg': 'Nội dung trang chủ',
    'halink_header_product_wg': 'Banner trang sản phẩm',
    'halink_footer0_wg': 'Footer top',
    'halink_footer1_wg': 'Footer middle',
    'halink_footer2_wg': 'Footer bottom',
    'halink_footer3_wg': 'Footer thanh toán',
    'halink_tab1_wg': 'Tab giải thưởng',
    'halink_tab2_wg': 'Tab cảm nhận khách hàng',
    'halink_tab3_wg': 'Tab ưu đãi - sự kiện',
    'halink_tab4_wg': 'Tab hình ảnh - video',
    'halink_tab5_wg': 'Tab tin tức & thư viện - video',
}

# Vài field khai báo type='text' nhưng thực chất lưu tên file ảnh đơn (Logo, Ảnh bản
# đồ...) — không tự nhận diện được qua type nên phải liệt kê thủ công (widget_type, field_name).
SINGLE_IMAGE_FIELDS = {
    ('halink_widget_company_info', 'halink_widget_input_content1'),
    ('halink_widget_map', 'halink_widget_input_content1'),
    ('halink_widget_text', 'halink_widget_input_content1'),
    ('halink_widget_text_layout', 'halink_widget_input_content1'),
}


def _idcat_member_filter(category_id):
    cid = str(category_id)
    return (
        Q(idcat=cid)
        | Q(idcat__startswith=f'{cid},')
        | Q(idcat__endswith=f',{cid}')
        | Q(idcat__contains=f',{cid},')
    )


def _image_url(request, filename):
    if not filename:
        return None
    rel_path = filename if '/' in filename else f'{IMAGE_SUBFOLDER}/{filename}'
    return build_media_url(request, rel_path)


def _resolve_posts_by_idcat(idcat_list, post_type, request, lang, limit=None):
    if not idcat_list:
        return []
    q = Q()
    for cid in idcat_list:
        q |= _idcat_member_filter(cid)
    queryset = HalinkPost.objects.filter(q, post_type=post_type, ticlock='0').order_by('sort', '-date')
    if limit:
        queryset = queryset[:limit]
    serializer = PostSummarySerializer(queryset, many=True, context={'request': request})
    return serializer.data


def _resolve_field_value(widget_type, field, fields_dict, request, lang):
    """Trả về giá trị đã xử lý cho 1 field, theo đúng `type`/`multilang` khai báo trong widgets_config.py."""
    name = field['name']

    if field.get('multilang'):
        value = fields_dict.get(f'{name}_lg_{lang}') or fields_dict.get(f'{name}_lg_vi') or ''
        return value

    field_type = field.get('type', 'text')
    raw_value = fields_dict.get(name, '')

    if field_type == 'image_list':
        names = [n.strip() for n in raw_value.split(',') if n.strip()]
        return [_image_url(request, n) for n in names]

    if (widget_type, name) in SINGLE_IMAGE_FIELDS:
        return _image_url(request, raw_value)

    if field_type == 'select_menu':
        if not raw_value:
            return None
        menu = HalinkMenu.objects.filter(Id=raw_value).first()
        if not menu:
            return None
        return build_menu_tree(menu.content_menu, lang)

    if field_type == 'select_postcat':
        if not raw_value:
            return {'idcat': None, 'items': []}
        return {'idcat': raw_value, 'items': _resolve_posts_by_idcat([raw_value], 'post', request, lang)}

    if field_type == 'select_productcat':
        if not raw_value:
            return {'idcat': None, 'items': []}
        return {'idcat': raw_value, 'items': _resolve_posts_by_idcat([raw_value], 'product', request, lang)}

    if widget_type == 'halink_widget_post_by_multicat' and name == 'halink_widget_input_content':
        idcat_list = [c.strip() for c in raw_value.split(',') if c.strip()]
        return {'idcat_list': idcat_list, 'items': _resolve_posts_by_idcat(idcat_list, 'post', request, lang)}

    # Dọn rác thẻ song ngữ cũ ([[[:vi]]]...[[[:end_vi]]]) còn sót lại trong dữ liệu đã lưu
    # trước đây (lúc field này còn khai báo multilang:True) - clean_lang không đổi gì
    # nếu chuỗi không có thẻ, nên an toàn áp dụng cho mọi field text/textarea còn lại.
    return clean_lang(raw_value, lang)


def _get_widget_type(instance_id):
    for key in AVAILABLE_WIDGETS:
        if instance_id.startswith(key):
            return key
    return None


def resolve_sidebar_widgets(position_id, request, lang):
    """
    Đọc đúng các widget đang gắn ở `position_id` (theo đúng thứ tự đã sắp trong
    Quản lý Widgets), trả về list đã gói sẵn dữ liệu cho FE. `position_id` không hợp
    lệ -> trả None để view trả 404.
    """
    if position_id not in VALID_POSITIONS:
        return None

    widgets_meta = HalinkMeta.objects.filter(meta_type='widgets').first()
    if not widgets_meta or not widgets_meta.meta_value:
        return []

    try:
        sidebar_mapping = json.loads(widgets_meta.meta_value)
    except (ValueError, TypeError):
        return []

    instance_ids = sidebar_mapping.get(position_id) or []
    if isinstance(instance_ids, str):
        instance_ids = [i.strip() for i in instance_ids.split(',') if i.strip()]

    result = []
    for instance_id in instance_ids:
        widget_type = _get_widget_type(instance_id)
        widget_def = AVAILABLE_WIDGETS.get(widget_type) if widget_type else None
        if not widget_def:
            continue

        content_meta = HalinkMeta.objects.filter(meta_type='widget_content', meta_title=instance_id).first()
        fields_dict = {}
        if content_meta and content_meta.meta_value:
            try:
                fields_list = json.loads(content_meta.meta_value)
                fields_dict = {f.get('name'): f.get('value', '') for f in fields_list}
            except (ValueError, TypeError):
                fields_dict = {}

        data = {}
        for field in widget_def['fields']:
            try:
                data[field['name']] = _resolve_field_value(widget_type, field, fields_dict, request, lang)
            except Exception:
                # 1 field lỗi (vd: trỏ tới chuyên mục đã xoá) không được làm hỏng cả response
                data[field['name']] = None

        result.append({
            'type': widget_type,
            'type_label': widget_def['name'],
            'data': data,
        })

    return result
