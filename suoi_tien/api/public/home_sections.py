"""
Resolver cho "Nội dung Trang chủ" — 15 khối cố định (tầng 2-15), thay cho hệ thống
Widget kéo-thả generic ở vị trí `halink_home_wg`. Mỗi khối thuộc 1 trong 3 nhóm:
- A: gắn cố định 1 Bài viết/Trang có sẵn.
- B: liệt kê bài viết theo 1 hoặc nhiều chuyên mục.
- C: nội dung tĩnh (text/ảnh/link) nhập trực tiếp, không liên quan bài viết nào.

Xem suoi_tien/views/home_sections_config.py (HOME_SECTIONS) cho định nghĩa 15 khối
và nơi admin nhập/lưu dữ liệu.
"""
import json

from suoi_tien.models import HalinkMeta, HalinkPost
from suoi_tien.views.home_sections_config import HOME_SECTIONS, META_TYPE
from .widgets import _image_url, _resolve_posts_by_idcat
from .serializers import PostDetailSerializer


def _load_section_raw(section_key):
    meta = HalinkMeta.objects.filter(meta_type=META_TYPE, meta_title=section_key).first()
    if not meta or not meta.meta_value:
        return {}
    try:
        return json.loads(meta.meta_value)
    except (ValueError, TypeError):
        return {}


def _resolve_group_a(data_raw, request, lang):
    post_id = data_raw.get('post_id')
    if not post_id:
        return {'post': None}
    post = HalinkPost.objects.filter(Id=post_id, ticlock='0').first()
    if not post:
        return {'post': None}
    serializer = PostDetailSerializer(post, context={'request': request})
    return {'post': serializer.data}


def _resolve_group_b(data_raw, request, lang):
    idcat_list = data_raw.get('idcat_list') or []
    title = data_raw.get('title', '')
    limit = data_raw.get('limit')
    items = _resolve_posts_by_idcat(idcat_list, 'post', request, lang, limit=limit)
    return {'idcat_list': idcat_list, 'title': title, 'items': items}


def _resolve_group_b_product(data_raw, request, lang):
    idcat_list = data_raw.get('idcat_list') or []
    title = data_raw.get('title', '')
    limit = data_raw.get('limit')
    items = _resolve_posts_by_idcat(idcat_list, 'product', request, lang, limit=limit)
    return {'idcat_list': idcat_list, 'title': title, 'items': items}


def _resolve_group_c(section_def, data_raw, request, lang):
    result = {}
    for field in section_def.get('fields', []):
        name = field['name']
        field_type = field.get('type', 'text')

        if field.get('multilang'):
            result[name] = data_raw.get(f'{name}_lg_{lang}') or data_raw.get(f'{name}_lg_vi') or ''
            continue

        if field_type == 'link_list':
            result[name] = data_raw.get(name) or []
            continue

        raw_value = data_raw.get(name, '')
        if field_type == 'image':
            result[f'{name}_url'] = _image_url(request, raw_value)
        elif field_type == 'image_list':
            names = [n.strip() for n in raw_value.split(',') if n.strip()] if raw_value else []
            urls = [_image_url(request, n) for n in names]
            result[name] = urls
            result['image_url'] = urls[0] if urls else ''
        else:
            result[name] = raw_value
    return result


def resolve_home_section(section_key, request, lang='vi'):
    """Trả {'section_key', 'group', 'name', 'data', '_is_hidden'} cho 1 khối, hoặc None nếu section_key không hợp lệ."""
    section_def = HOME_SECTIONS.get(section_key)
    if not section_def:
        return None

    data_raw = _load_section_raw(section_key)
    if data_raw.get('_is_hidden'):
        return {'section_key': section_key, 'group': section_def['group'], '_is_hidden': True}

    group = section_def['group']

    if group == 'A':
        data = _resolve_group_a(data_raw, request, lang)
    elif group == 'B':
        data = _resolve_group_b(data_raw, request, lang)
    elif group == 'B_PRODUCT':
        data = _resolve_group_b_product(data_raw, request, lang)
    else:
        data = _resolve_group_c(section_def, data_raw, request, lang)

    name = data_raw.get('_custom_name') or section_def['name']
    return {'section_key': section_key, 'group': group, 'name': name, 'data': data, '_is_hidden': False}


def resolve_all_home_sections(request, lang='vi'):
    """Trả list các khối theo thứ tự khai báo trong HOME_SECTIONS. Khối bị _is_hidden=True sẽ bị bỏ qua."""
    result = []
    for section_key in HOME_SECTIONS:
        try:
            section = resolve_home_section(section_key, request, lang)
            if section and section.get('_is_hidden'):
                continue
        except Exception:
            section = {'section_key': section_key, 'group': HOME_SECTIONS[section_key]['group'],
                       'name': HOME_SECTIONS[section_key]['name'], 'data': None}
        if section:
            result.append(section)
    return result
