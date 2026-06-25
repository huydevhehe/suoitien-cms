import json

from suoi_tien.models import HalinkPost
from suoi_tien.utils import clean_lang

# Định dạng lưu THẬT của PHP gốc (xem halink_save_menu() trong halink-admin/public/js/main.js):
# content_menu là 1 mảng JSON các chuỗi, mỗi chuỗi 7 phần nối bằng "_***_":
# id, type, link_url, link_text, level, title, blank.
MENU_FIELD_SEPARATOR = '_***_'
MENU_KIND_LINK = 'link'


def _parse_menu_items(content_menu):
    """Tách `content_menu` thành list dict theo đúng định dạng PHP gốc (7 phần/mục)."""
    if not content_menu:
        return []

    try:
        raw_items = json.loads(content_menu)
    except (ValueError, TypeError):
        raw_items = None

    if isinstance(raw_items, list):
        parsed = []
        for raw in raw_items:
            parts = str(raw).split(MENU_FIELD_SEPARATOR)
            if len(parts) != 7:
                continue
            item_id, kind, link_url, link_text, level_str, title, blank = parts
            try:
                level = int(level_str)
            except ValueError:
                level = 0
            parsed.append({
                'id': item_id, 'kind': kind, 'link_url': link_url,
                'link_text': link_text, 'level': level, 'title': title,
                'blank': blank == '1',
            })
        return parsed

    # Dữ liệu cũ lưu nhầm dạng "id***kind***level" ngăn bởi dấu phẩy (do 1 bản
    # code trước đây lưu sai, không đúng định dạng PHP gốc) - khôi phục tạm để
    # không mất dữ liệu, FE vẫn đọc được link/title/blank mặc định.
    OLD_KIND_MAP = {'_page_': 'pagehtml', '_news_': 'catnews', '_productcat_': 'catelog', '_link_': 'link'}
    parsed = []
    for raw in (content_menu or '').split(','):
        raw = raw.strip()
        if not raw:
            continue
        parts = raw.split('***')
        if len(parts) != 3:
            continue
        item_id, old_kind, level_str = parts
        kind = OLD_KIND_MAP.get(old_kind, 'pagehtml')
        try:
            level = int(level_str)
        except ValueError:
            level = 0
        parsed.append({
            'id': item_id, 'kind': kind,
            'link_url': item_id if kind == MENU_KIND_LINK else '0',
            'link_text': '0', 'level': level, 'title': item_id, 'blank': False,
        })
    return parsed


def build_menu_tree(content_menu, lang='vi'):
    """
    Dựng cây menu lồng nhau từ `content_menu` (định dạng PHP gốc thật).
    `lang` ('vi'/'en') chọn ngôn ngữ hiển thị tiêu đề menu trỏ tới bài viết.
    """
    parsed_items = _parse_menu_items(content_menu)

    post_ids = {
        int(item['id']) for item in parsed_items
        if item['kind'] != MENU_KIND_LINK and str(item['id']).isdigit()
    }
    posts_by_id = {
        post.Id: post for post in HalinkPost.objects.filter(Id__in=post_ids)
    } if post_ids else {}

    roots = []
    last_node_at_depth = {}

    for item in parsed_items:
        node = _build_menu_node(item, posts_by_id, lang)
        depth = item['level']

        parent = last_node_at_depth.get(depth - 1)
        if depth == 0 or parent is None:
            roots.append(node)
        else:
            parent['children'].append(node)

        last_node_at_depth[depth] = node
        for deeper_depth in [d for d in last_node_at_depth if d > depth]:
            del last_node_at_depth[deeper_depth]

    return roots


def _build_menu_node(item, posts_by_id, lang='vi'):
    node = {'type': item['kind'], 'children': [], 'target_blank': item['blank']}

    if item['kind'] == MENU_KIND_LINK:
        node.update(title=clean_lang(item['title'], lang), url=item['link_url'], alias=None, post_id=None)
        return node

    post = posts_by_id.get(int(item['id'])) if str(item['id']).isdigit() else None
    if post:
        node.update(title=clean_lang(post.title_vn, lang), url=None, alias=post.alias, post_id=post.Id)
    else:
        node.update(title=clean_lang(item['title'], lang) or f"#{item['id']}", url=None, alias=None, post_id=item['id'])
    return node
