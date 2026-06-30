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
    subtitle = data_raw.get('subtitle', '')
    limit = data_raw.get('limit')
    items = _resolve_posts_by_idcat(idcat_list, 'post', request, lang, limit=limit)
    return {'idcat_list': idcat_list, 'title': title, 'subtitle': subtitle, 'items': items}


def _resolve_group_b_product(data_raw, request, lang):
    idcat_list = data_raw.get('idcat_list') or []
    title = data_raw.get('title', '')
    subtitle = data_raw.get('subtitle', '')
    limit = data_raw.get('limit')
    items = _resolve_posts_by_idcat(idcat_list, 'product', request, lang, limit=limit)
    return {'idcat_list': idcat_list, 'title': title, 'subtitle': subtitle, 'items': items}


def _resolve_group_b_product_cats(data_raw, request, lang):
    cat_ids = data_raw.get('cat_ids') or []
    categories = []
    for idcat_str in cat_ids:
        try:
            cat_obj = HalinkPost.objects.filter(Id=int(idcat_str)).first()
            cat_title = cat_obj.title if cat_obj else ''
        except (ValueError, TypeError):
            cat_title = ''
        items = _resolve_posts_by_idcat([str(idcat_str)], 'product', request, lang, limit=6)
        categories.append({
            'idcat': int(idcat_str),
            'cat_title': cat_title,
            'items': items,
        })
    return {'categories': categories}


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

        if field_type == 'cat_list':
            items = data_raw.get(name) or []
            limit_cats_raw = data_raw.get('limit_cats', '')
            limit_per_cat_raw = data_raw.get('limit_per_cat', '')
            try:
                limit_cats = int(limit_cats_raw) if str(limit_cats_raw).strip() else None
            except (ValueError, TypeError):
                limit_cats = None
            try:
                limit_per_cat = int(limit_per_cat_raw) if str(limit_per_cat_raw).strip() else None
            except (ValueError, TypeError):
                limit_per_cat = None
            if limit_cats:
                items = items[:limit_cats]
            cats_with_posts = []
            for item in items:
                cat_id = item.get('cat_id')
                if not cat_id:
                    continue
                posts = _resolve_posts_by_idcat([str(cat_id)], 'post', request, lang, limit=limit_per_cat)
                cats_with_posts.append({
                    'cat_id': cat_id,
                    'title': item.get('title', ''),
                    'posts': posts,
                })
            result[name] = cats_with_posts
            continue

        raw_value = data_raw.get(name, '')
        if field_type == 'image':
            result[f'{name}_url'] = _image_url(request, raw_value)
        elif field_type == 'image_list':
            names = [n.strip() for n in raw_value.split(',') if n.strip()] if raw_value else []
            urls = [_image_url(request, n) for n in names]
            result[name] = urls
            result['image_url'] = urls[0] if urls else ''
        elif field_type == 'select_post':
            result[name] = raw_value
            if raw_value:
                post = HalinkPost.objects.filter(Id=raw_value, ticlock='0').first()
                if post and post.alias:
                    # Tạo thêm 1 trường {name}_url (hoặc post_link) để FE dễ lấy
                    result[f'{name}_url'] = f'/bai-viet/{post.alias}'
                    # Ghi đè hoặc cung cấp thêm 1 link chung nếu cần
                    result['post_link'] = f'/bai-viet/{post.alias}'
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
