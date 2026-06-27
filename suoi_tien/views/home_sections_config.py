"""
Cấu hình "Cấu hình Trang chủ" theo các khối cố định (tầng 2-15 + 4 cột Footer ở
tầng 16), thay cho hệ thống Widget kéo-thả generic ở vị trí `halink_home_wg` và
`halink_footer2_wg`. Tầng 1 (Header/Menu) không thuộc phạm vi này. Xem
suoi_tien/api/public/home_sections.py cho phần resolver Public API tương ứng.
"""
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from django.contrib import admin

from suoi_tien.models import HalinkMeta, HalinkPost
from suoi_tien.utils import clean_lang

META_TYPE = 'home_section'

# 3 nhóm theo cách lấy dữ liệu (xem suoi_tien/api/public/home_sections.py để biết
# cách resolve từng nhóm):
# - A: gắn cố định 1 Bài viết/Trang có sẵn (chỉ cần post_id).
# - B: liệt kê bài viết theo 1 hoặc nhiều chuyên mục (idcat_list).
# - C: nội dung tĩnh nhập trực tiếp (field khai báo riêng từng khối).
HOME_SECTIONS = {
    # ---- Nhóm C: nội dung tĩnh ----
    'section_02_dat_ve': {
        'name': 'Tầng 2 - Đặt vé / Tra vé nhanh',
        'group': 'C',
        'fields': [
            {'name': 'link_dat_ve', 'label': 'Link nút "ĐẶT VÉ" (Ví dụ: /chon-ve)', 'type': 'text', 'multilang': False},
            {'name': 'link_tra_cuu', 'label': 'Link nút "TRA CỨU VÉ" (Ví dụ: /tra-cuu)', 'type': 'text', 'multilang': False},
        ],
    },
    'section_03_banner_gioithieu': {
        'name': 'Tầng 3 - Banner Slider',
        'group': 'C',
        'fields': [
            {'name': 'banner_images', 'label': 'Danh sách ảnh Banner Slider', 'type': 'image_list', 'multilang': False},
            {'name': 'banner_link', 'label': 'Link khi bấm vào Banner', 'type': 'text', 'multilang': False},
        ],
    },
    'section_05_dichvu': {
        'name': 'Tầng 5 - Du lịch văn hóa Suối Tiên',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'subtitle', 'label': 'Tiêu đề phụ', 'type': 'text', 'multilang': True},
            {'name': 'content', 'label': 'Nội dung ngắn (hỗ trợ xuống dòng bằng <br>)', 'type': 'textarea', 'multilang': True},
            {'name': 'link', 'label': 'Đường dẫn liên kết nút "TÌM HIỂU THÊM" (Ví dụ: /du-lich-van-hoa)', 'type': 'text', 'multilang': False},
            {'name': 'images', 'label': 'Danh sách ảnh Slider đứng (thêm bao nhiêu ảnh cũng được)', 'type': 'image_list', 'multilang': False},
        ],
    },
    'section_14_bando': {
        'name': 'Tầng 14 - Bản đồ khu vực',
        'group': 'C',
        'fields': [
            {'name': 'map_image', 'label': 'Ảnh sơ đồ bản đồ', 'type': 'image', 'multilang': False},
            {'name': 'map_link', 'label': 'Link "Xem bản đồ tương tác"', 'type': 'text', 'multilang': False},
        ],
    },
    'section_15_doitac': {
        'name': 'Tầng 15 - Đối tác đồng hành / Gallery',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'images', 'label': 'Danh sách logo đối tác (thêm bao nhiêu cũng được)', 'type': 'image_list', 'multilang': False},
        ],
    },
    'section_06_van_hoa': {
        'name': 'Tầng 6 - Trải nghiệm văn hóa lịch sử tâm linh',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề dòng 1 (Chữ màu trắng, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'subtitle', 'label': 'Tiêu đề dòng 2 (Chữ màu xanh lá, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'description', 'label': 'Tiêu đề phụ / Chú thích (Bỏ trống sẽ tự ẩn, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'link', 'label': 'Đường dẫn (Link nút "TÌM HIỂU THÊM" / Click Banner)', 'type': 'text', 'multilang': False},
            {'name': 'images', 'label': 'Danh sách ảnh Banner background (thêm nhiều ảnh bự làm slider)', 'type': 'image_list', 'multilang': False},
        ],
    },
    'section_07_tohop150': {
        'name': 'Tầng 7 - Tổ hợp 150 công trình',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề dòng 1 (Chữ màu trắng, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'subtitle', 'label': 'Tiêu đề dòng 2 (Chữ màu xanh lá, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'description', 'label': 'Tiêu đề phụ / Chú thích (Bỏ trống sẽ tự ẩn, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'link', 'label': 'Đường dẫn (Link nút "TÌM HIỂU THÊM" / Click Banner)', 'type': 'text', 'multilang': False},
            {'name': 'images', 'label': 'Danh sách ảnh Banner background (thêm nhiều ảnh bự làm slider)', 'type': 'image_list', 'multilang': False},
        ],
    },
    'section_08_bien_tien_dong': {
        'name': 'Tầng 8 - Công viên nước Biển Tiên Đồng Ngọc Nữ',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề dòng 1 (Chữ màu trắng, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'subtitle', 'label': 'Tiêu đề dòng 2 (Chữ màu xanh lá, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'description', 'label': 'Tiêu đề phụ / Chú thích (Bỏ trống sẽ tự ẩn, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'link', 'label': 'Đường dẫn (Link nút "TÌM HIỂU THÊM" / Click Banner)', 'type': 'text', 'multilang': False},
            {'name': 'images', 'label': 'Danh sách ảnh Banner background (thêm nhiều ảnh bự làm slider)', 'type': 'image_list', 'multilang': False},
        ],
    },
    'section_09_farm': {
        'name': 'Tầng 9 - Suối Tiên Farm',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề dòng 1 (Chữ màu trắng, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'subtitle', 'label': 'Tiêu đề dòng 2 (Chữ màu xanh lá, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'description', 'label': 'Tiêu đề phụ / Chú thích (Bỏ trống sẽ tự ẩn, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'link', 'label': 'Đường dẫn (Link nút "TÌM HIỂU THÊM" / Click Banner)', 'type': 'text', 'multilang': False},
            {'name': 'images', 'label': 'Danh sách ảnh Banner background (thêm nhiều ảnh bự làm slider)', 'type': 'image_list', 'multilang': False},
        ],
    },
    'section_10a_amthuc': {
        'name': 'Tầng 10a - Ẩm thực Suối Tiên',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề dòng 1 (Chữ màu trắng, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'subtitle', 'label': 'Tiêu đề dòng 2 (Chữ màu xanh lá, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'description', 'label': 'Tiêu đề phụ / Chú thích (Bỏ trống sẽ tự ẩn, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'link', 'label': 'Đường dẫn (Link nút "TÌM HIỂU THÊM" / Click Banner)', 'type': 'text', 'multilang': False},
            {'name': 'images', 'label': 'Danh sách ảnh Banner background (thêm nhiều ảnh bự làm slider)', 'type': 'image_list', 'multilang': False},
        ],
    },
    'section_10b_showdien': {
        'name': 'Tầng 10b - Show diễn & Trải nghiệm về đêm',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề dòng 1 (Chữ màu trắng, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'subtitle', 'label': 'Tiêu đề dòng 2 (Chữ màu xanh lá, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'description', 'label': 'Tiêu đề phụ / Chú thích (Bỏ trống sẽ tự ẩn, hỗ trợ mã HTML)', 'type': 'textarea', 'multilang': True},
            {'name': 'link', 'label': 'Đường dẫn (Link nút "TÌM HIỂU THÊM" / Click Banner)', 'type': 'text', 'multilang': False},
            {'name': 'images', 'label': 'Danh sách ảnh Banner background (thêm nhiều ảnh bự làm slider)', 'type': 'image_list', 'multilang': False},
        ],
    },
    # ---- Nhóm A: gắn 1 bài viết cố định ----
    'section_11_combo': {'name': 'Tầng 11 - Gợi ý Combo phù hợp', 'group': 'B_PRODUCT'},

    # ---- Nhóm B: liệt kê theo chuyên mục ----
    'section_04_uudai': {'name': 'Tầng 4 - Tin tức Ưu đãi & sự kiện', 'group': 'B'},
    'section_12_teambuilding': {'name': 'Tầng 12 - Các dịch vụ thương mại', 'group': 'B'},
    'section_13_camnang': {'name': 'Tầng 13 - Cẩm nang du lịch', 'group': 'B'},

    # ---- Tầng 16: 4 cột Footer (gộp chung vào đây cho gọn, thay cho halink_footer2_wg) ----
    'section_16a_ve_chung_toi': {
        'name': 'Tầng 16a - Footer: Về chúng tôi',
        'group': 'C',
        'is_footer': True,
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề cột', 'type': 'text', 'multilang': True},
            {'name': 'items', 'label': 'Danh sách link (thêm bao nhiêu cũng được)', 'type': 'link_list', 'multilang': False},
        ],
    },
    'section_16b_dieu_khoan': {
        'name': 'Tầng 16b - Footer: Điều khoản - Chính sách',
        'group': 'C',
        'is_footer': True,
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề cột', 'type': 'text', 'multilang': True},
            {'name': 'items', 'label': 'Danh sách link (thêm bao nhiêu cũng được)', 'type': 'link_list', 'multilang': False},
        ],
    },
    'section_16c_lien_he': {
        'name': 'Tầng 16c - Footer: Liên hệ ngay',
        'group': 'C',
        'is_footer': True,
        'fields': [
            {'name': 'logo', 'label': 'Logo/Ảnh', 'type': 'image', 'multilang': False},
            {'name': 'address', 'label': 'Địa chỉ', 'type': 'text', 'multilang': True},
            {'name': 'phone', 'label': 'Điện thoại', 'type': 'text', 'multilang': False},
            {'name': 'email', 'label': 'Email', 'type': 'text', 'multilang': False},
        ],
    },
    'section_16d_gioi_thieu': {
        'name': 'Tầng 16d - Footer: Giới thiệu',
        'group': 'C',
        'is_footer': True,
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'content', 'label': 'Nội dung giới thiệu công ty', 'type': 'textarea', 'multilang': True},
        ],
    },
}


def _load_section_values():
    """Đọc toàn bộ giá trị đã lưu của 15 khối, trả dict section_key -> dict đã parse JSON."""
    values = {}
    for meta in HalinkMeta.objects.filter(meta_type=META_TYPE):
        if not meta.meta_title:
            continue
        try:
            values[meta.meta_title] = json.loads(meta.meta_value) if meta.meta_value else {}
        except (ValueError, TypeError):
            values[meta.meta_title] = {}
    return values


def _group_sections_for_display():
    """Gom 19 khối thành 4 dải hiển thị ngang: Nhóm C (nội dung tĩnh, trừ Footer) ->
    Nhóm B (theo chuyên mục) -> Nhóm A (gắn bài viết) -> Footer (4 cột) - đỡ phải
    cuộn dài 1 cột dọc duy nhất."""
    rows = {'C': [], 'B': [], 'A': [], 'FOOTER': []}
    for key, section in HOME_SECTIONS.items():
        bucket = 'FOOTER' if section.get('is_footer') else section['group']
        rows[bucket].append((key, section))
    return rows


@staff_member_required
def home_sections_view(request):
    section_values = _load_section_values()

    posts_for_select = [
        {'Id': p['Id'], 'title': clean_lang(p['title_vn']) or f"Bài viết #{p['Id']}", 'alias': p['alias'] or ''}
        for p in HalinkPost.objects.filter(ticlock='0').exclude(post_type='product').exclude(post_type='postcat').values('Id', 'title_vn', 'alias').order_by('title_vn')
    ]

    categories_for_select = [
        {'Id': c['Id'], 'title': clean_lang(c['title_vn']) or f"Chuyên mục #{c['Id']}"}
        for c in HalinkPost.objects.filter(post_type='postcat', ticlock='0').values('Id', 'title_vn').order_by('title_vn')
    ]

    product_categories_for_select = [
        {'Id': c['Id'], 'title': clean_lang(c['title_vn']) or f"Chuyên mục SP #{c['Id']}"}
        for c in HalinkPost.objects.filter(post_type='productcat', ticlock='0').values('Id', 'title_vn').order_by('title_vn')
    ]

    context = {
        'section_rows': _group_sections_for_display(),
        'section_values': section_values,
        'posts_for_select': posts_for_select,
        'categories_for_select': categories_for_select,
        'product_categories_for_select': product_categories_for_select,
        'title': 'Cấu hình Trang chủ',
    }
    context.update(admin.site.each_context(request))
    return render(request, 'admin/home_sections.html', context)


@csrf_exempt
@staff_member_required
def home_sections_save_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Chỉ chấp nhận phương thức POST'}, status=400)

    try:
        data = json.loads(request.body)
        sections_data = data.get('sections', {})  # Map: section_key -> {field: value, ...}

        with transaction.atomic():
            for section_key, fields in sections_data.items():
                if section_key not in HOME_SECTIONS:
                    continue

                meta_item = HalinkMeta.objects.filter(meta_type=META_TYPE, meta_title=section_key).first()
                if not meta_item:
                    meta_item = HalinkMeta(meta_type=META_TYPE, meta_title=section_key, ticlock=0)

                meta_item.meta_value = json.dumps(fields, ensure_ascii=False)
                meta_item.date = timezone.now()
                meta_item.save()

        return JsonResponse({'status': 'success', 'message': 'Đã lưu cấu hình Trang chủ thành công!'})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'status': 'error', 'message': f'Lỗi hệ thống: {str(e)}'}, status=500)
