from suoi_tien.models import HalinkPost
from suoi_tien.utils import clean_lang

MENU_ITEM_SEPARATOR = '***'
MENU_KIND_LINK = '_link_'


def _parse_menu_items(content_menu):
    """Tách chuỗi content_menu thô thành list (target, kind, depth)."""
    parsed = []
    for raw in (content_menu or '').split(','):
        raw = raw.strip()
        if not raw:
            continue
        parts = raw.split(MENU_ITEM_SEPARATOR)
        if len(parts) != 3:
            continue
        target, kind, depth_str = parts
        try:
            depth = int(depth_str)
        except ValueError:
            depth = 0
        parsed.append((target, kind, depth))
    return parsed


def build_menu_tree(content_menu):
    """
    Dựng cây menu lồng nhau từ chuỗi thô `content_menu` (xem ke_hoach_menu_builder.md):
    mỗi mục có dạng "ID_hoặc_Link***Loại_Menu***Độ_Sâu", ngăn cách bằng dấu phẩy.
    """
    parsed_items = _parse_menu_items(content_menu)

    post_ids = {int(target) for target, kind, _ in parsed_items
                if kind != MENU_KIND_LINK and target.isdigit()}
    posts_by_id = {
        post.Id: post
        for post in HalinkPost.objects.filter(Id__in=post_ids)
    } if post_ids else {}

    roots = []
    last_node_at_depth = {}

    for target, kind, depth in parsed_items:
        node = _build_menu_node(target, kind, posts_by_id)

        parent = last_node_at_depth.get(depth - 1)
        if depth == 0 or parent is None:
            roots.append(node)
        else:
            parent['children'].append(node)

        last_node_at_depth[depth] = node
        for deeper_depth in [d for d in last_node_at_depth if d > depth]:
            del last_node_at_depth[deeper_depth]

    return roots


def _build_menu_node(target, kind, posts_by_id):
    node = {'type': kind.strip('_'), 'children': []}

    if kind == MENU_KIND_LINK:
        node.update(title=target, url=target, alias=None, post_id=None)
        return node

    post = posts_by_id.get(int(target)) if target.isdigit() else None
    if post:
        node.update(title=clean_lang(post.title_vn), url=None, alias=post.alias, post_id=post.Id)
    else:
        node.update(title=f"#{target}", url=None, alias=None, post_id=target)
    return node
