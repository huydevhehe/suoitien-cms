import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from suoi_tien.models import HalinkMeta
from suoi_tien.views.page_sections_config import PAGES
from suoi_tien.api.public.home_sections import _resolve_group_a, _resolve_group_b, _resolve_group_b_product

META_TYPE = 'home_section'

@extend_schema(
    summary="Lấy cấu hình các sections của một trang (Trang chủ, Giới thiệu...)",
    description="API dùng chung cho tất cả các trang được tạo cấu hình động. Truyền page_key (VD: 'home', 'gioi-thieu') để nhận lại dữ liệu.",
    parameters=[
        OpenApiParameter(name='lang', description='Ngôn ngữ (vi / en)', required=False, type=OpenApiTypes.STR, default='vi', location=OpenApiParameter.QUERY)
    ],
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(['GET'])
def get_page_sections(request, page_key):
    """
    API dùng chung cho tất cả các trang. Trả về toàn bộ các khối (sections) của trang.
    - Với trang 'home', đọc các bản ghi không có namespace.
    - Với trang khác, đọc các bản ghi có namespace 'page_key:section_key'.
    """
    if page_key not in PAGES:
        return Response({'status': 'error', 'message': 'Không tìm thấy cấu hình cho trang này'}, status=404)

    page_config = PAGES[page_key]['sections']
    
    # 1. Đọc dữ liệu thô từ DB
    raw_data = {}
    
    # Nếu là trang chủ, quét những cái không có dấu ':'
    if page_key == 'home':
        metas = HalinkMeta.objects.filter(meta_type=META_TYPE)
        for meta in metas:
            if meta.meta_title and ':' not in meta.meta_title:
                try:
                    raw_data[meta.meta_title] = json.loads(meta.meta_value) if meta.meta_value else {}
                except (ValueError, TypeError):
                    pass
    else:
        # Nếu là trang con, quét những cái bắt đầu bằng page_key:
        prefix = f"{page_key}:"
        metas = HalinkMeta.objects.filter(meta_type=META_TYPE, meta_title__startswith=prefix)
        for meta in metas:
            section_key = meta.meta_title[len(prefix):]
            try:
                raw_data[section_key] = json.loads(meta.meta_value) if meta.meta_value else {}
            except (ValueError, TypeError):
                pass

    # 2. Map dữ liệu vào cấu hình chuẩn và resolve Group A, B nếu có
    resolved_sections = {}
    for section_key, config in page_config.items():
        if section_key not in raw_data:
            continue

        data = raw_data[section_key]
        if data.get('_is_hidden'):
            continue  # Bỏ qua nếu admin chọn Ẩn khối

        # Xử lý custom name
        name = data.get('_custom_name') or config['name']

        # Dữ liệu cơ bản
        section_output = {
            'name': name,
            'group': config['group'],
            'is_footer': config.get('is_footer', False),
            'data': data,
            'resolved_data': None
        }

        # Bơm thêm dữ liệu động cho nhóm A và B
        lang = request.GET.get('lang', 'vi')
        if config['group'] == 'A':
            post_id = data.get('post_id')
            if post_id:
                section_output['resolved_data'] = _resolve_group_a(data, request, lang)
        elif config['group'] == 'B':
            cat_list = data.get('idcat_list')
            if cat_list:
                section_output['resolved_data'] = _resolve_group_b(data, request, lang)
        elif config['group'] == 'B_PRODUCT':
            cat_list = data.get('idcat_list')
            if cat_list:
                section_output['resolved_data'] = _resolve_group_b_product(data, request, lang)

        resolved_sections[section_key] = section_output

    return Response({
        'status': 'success',
        'page_key': page_key,
        'page_name': PAGES[page_key]['name'],
        'sections': resolved_sections
    })
