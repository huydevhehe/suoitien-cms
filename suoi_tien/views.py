import os
import re
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from core.settings import BASE_DIR
from suoi_tien.models import HalinkWebsite, HalinkMeta, HalinkMenu, HalinkPost
from suoi_tien.utils import clean_lang
from django.contrib import admin

# Định nghĩa các widget sẵn có và các trường dữ liệu tương ứng của chúng
AVAILABLE_WIDGETS = {
    'halink_widget_banner': {
        'name': 'Banner quảng cáo',
        'desc': 'Hiển thị ảnh Banner quảng cáo động theo từng khu vực.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_link', 'label': 'Đường dẫn liên kết (Link)', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content', 'label': 'Danh sách ảnh (ngăn cách bởi dấu phẩy)', 'type': 'textarea', 'multilang': False},
        ]
    },
    'halink_widget_company_info': {
        'name': 'Giới thiệu công ty',
        'desc': 'Hiển thị thông tin liên hệ, bản quyền ở chân trang (Footer).',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_title1', 'label': 'Địa chỉ', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_title2', 'label': 'Điện thoại', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_title3', 'label': 'Email', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content1', 'label': 'Logo công ty (tên file ảnh)', 'type': 'text', 'multilang': False},
        ]
    },
    'halink_widget_customer_reviews': {
        'name': 'Cảm nhận khách hàng',
        'desc': 'Hiển thị các phản hồi, đánh giá từ khách hàng (Testimonials).',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content', 'label': 'Danh sách ảnh đại diện (ngăn cách bởi dấu phẩy)', 'type': 'textarea', 'multilang': False},
            {'name': 'halink_widget_input_link', 'label': 'Ý kiến khách hàng (Họ tên|Ý kiến, mỗi dòng 1 người)', 'type': 'textarea', 'multilang': True},
        ]
    },
    'halink_widget_gallery': {
        'name': 'Gallery',
        'desc': 'Hiển thị lưới hình ảnh hoạt động của công viên.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content', 'label': 'Danh sách ảnh (ngăn cách bởi dấu phẩy)', 'type': 'textarea', 'multilang': False},
            {'name': 'halink_widget_input_link', 'label': 'Mô tả / Liên kết (mỗi dòng 1 liên kết hoặc nhãn)', 'type': 'textarea', 'multilang': True},
        ]
    },
    'halink_widget_gallery_popup': {
        'name': 'Gallery Popup',
        'desc': 'Hiển thị bộ sưu tập hình ảnh có hỗ trợ xem phóng to (Lightbox).',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_numtab', 'label': 'Số lượng Tab', 'type': 'text', 'multilang': False, 'default': '2'},
            {'name': 'halink_widget_input_tab', 'label': 'Tiêu đề các Tab (ngăn cách bởi dấu |)', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content1', 'label': 'Ảnh Tab 1 (ngăn cách bởi dấu phẩy)', 'type': 'textarea', 'multilang': False},
            {'name': 'halink_widget_input_content2', 'label': 'Ảnh Tab 2 (ngăn cách bởi dấu phẩy)', 'type': 'textarea', 'multilang': False},
            {'name': 'halink_widget_input_list_video', 'label': 'Danh sách link video Youtube (mỗi dòng 1 link)', 'type': 'textarea', 'multilang': False},
            {'name': 'halink_widget_input_link', 'label': 'Link xem thêm', 'type': 'text', 'multilang': True},
        ]
    },
    'halink_widget_htmlcode': {
        'name': 'HTML tùy chỉnh',
        'desc': 'Cho phép chèn mã HTML hoặc Javascript tùy biến.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content', 'label': 'Mã HTML/JS', 'type': 'textarea', 'multilang': False},
        ]
    },
    'halink_widget_imglist': {
        'name': 'List liên kết ảnh',
        'desc': 'Danh sách các đối tác liên kết hoặc chứng nhận chất lượng.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_title_link', 'label': 'Tiêu đề liên kết', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_link', 'label': 'Link liên kết', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content', 'label': 'Danh sách ảnh (ngăn cách bởi dấu phẩy)', 'type': 'textarea', 'multilang': False},
        ]
    },
    'halink_widget_map': {
        'name': 'Bản đồ',
        'desc': 'Nhúng bản đồ đường đi Google Maps.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content1', 'label': 'Ảnh bản đồ', 'type': 'text', 'multilang': False},
            {'name': 'halink_widget_input_link', 'label': 'Link Google Maps', 'type': 'text', 'multilang': False},
        ]
    },
    'halink_widget_menu': {
        'name': 'Thanh điều hướng (Menu)',
        'desc': 'Render menu điều hướng đa cấp linh hoạt.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content', 'label': 'Chọn Menu', 'type': 'select_menu', 'multilang': False},
        ]
    },
    'halink_widget_post_by_cat': {
        'name': 'Bài viết theo chuyên mục',
        'desc': 'Hiển thị danh sách các bài viết thuộc một danh mục cụ thể.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content', 'label': 'Chọn chuyên mục bài viết', 'type': 'select_postcat', 'multilang': False},
        ]
    },
    'halink_widget_post_by_multicat': {
        'name': 'Bài viết nhiều chuyên mục',
        'desc': 'Gom và hiển thị bài viết từ nhiều danh mục khác nhau.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content', 'label': 'Danh sách ID chuyên mục (ngăn cách bởi dấu phẩy)', 'type': 'text', 'multilang': False},
        ]
    },
    'halink_widget_product_by_cat': {
        'name': 'Sản phẩm theo danh mục',
        'desc': 'Hiển thị danh sách vé/ẩm thực thuộc một danh mục cụ thể.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content', 'label': 'Chọn danh mục sản phẩm', 'type': 'select_productcat', 'multilang': False},
        ]
    },
    'halink_widget_product_by_type': {
        'name': 'Sản phẩm theo loại',
        'desc': 'Lọc và hiển thị sản phẩm theo loại đặc thù.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content', 'label': 'Mã loại sản phẩm', 'type': 'text', 'multilang': False},
        ]
    },
    'halink_widget_productcat_slider': {
        'name': 'Slider danh mục sản phẩm',
        'desc': 'Slider chạy danh mục sản phẩm.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content', 'label': 'ID danh mục sản phẩm', 'type': 'text', 'multilang': False},
        ]
    },
    'halink_widget_slider': {
        'name': 'Trình chiếu Slider',
        'desc': 'Trình chiếu ảnh Slider trang chủ chính.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content', 'label': 'Danh sách ảnh (ngăn cách bởi dấu phẩy)', 'type': 'textarea', 'multilang': False},
            {'name': 'halink_widget_input_link', 'label': 'Link liên kết khi click', 'type': 'text', 'multilang': True},
        ]
    },
    'halink_widget_subscription': {
        'name': 'Form đăng ký nhận tin',
        'desc': 'Khối đăng ký nhận bản tin qua Email.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề chính', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_title1', 'label': 'Tiêu đề phụ/Mô tả', 'type': 'text', 'multilang': True},
        ]
    },
    'halink_widget_text': {
        'name': 'Mô tả ngắn (WYSIWYG)',
        'desc': 'Khối nhập văn bản tự do định dạng phong phú.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_title1', 'label': 'Tiêu đề phụ', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_link', 'label': 'Link xem thêm', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_runtext', 'label': 'Chữ chạy', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content', 'label': 'Nội dung hiển thị', 'type': 'textarea', 'multilang': True},
            {'name': 'halink_widget_input_content1', 'label': 'Ảnh đính kèm (tên file)', 'type': 'text', 'multilang': False},
        ]
    },
    'halink_widget_text_layout': {
        'name': 'Hộp nội dung cột',
        'desc': 'Nhập văn bản tự do chia cột hoặc danh sách ID sản phẩm.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề chính', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_title1', 'label': 'Tiêu đề phụ', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content', 'label': 'Mô tả cột 1', 'type': 'textarea', 'multilang': True},
            {'name': 'halink_widget_input_content2', 'label': 'Mô tả cột 2', 'type': 'textarea', 'multilang': True},
            {'name': 'halink_widget_input_content1', 'label': 'Ảnh nền', 'type': 'text', 'multilang': False},
            {'name': 'halink_widget_input_content3', 'label': 'Danh sách ID cột 1', 'type': 'text', 'multilang': False},
            {'name': 'halink_widget_input_content4', 'label': 'Danh sách ID cột 2', 'type': 'text', 'multilang': False},
        ]
    },
    'halink_widget_short_desc': {
        'name': 'Mô tả ngắn phụ',
        'desc': 'Khối giới thiệu ngắn công ty.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_content', 'label': 'Nội dung', 'type': 'textarea', 'multilang': True},
            {'name': 'halink_widget_input_content2', 'label': 'Mô tả chi tiết', 'type': 'textarea', 'multilang': True},
            {'name': 'halink_widget_input_address', 'label': 'Địa chỉ', 'type': 'text', 'multilang': True},
            {'name': 'halink_widget_input_phone', 'label': 'Điện thoại', 'type': 'text', 'multilang': False},
            {'name': 'halink_widget_input_email', 'label': 'Email', 'type': 'text', 'multilang': False},
        ]
    },
    'halink_widget_livemap': {
        'name': 'Bản đồ trực tiếp',
        'desc': 'Nhúng bản đồ trực tiếp.',
        'fields': [
            {'name': 'halink_widget_input_title', 'label': 'Tiêu đề', 'type': 'text', 'multilang': False},
        ]
    }
}

def get_active_theme():
    website = HalinkWebsite.objects.first()
    theme_key = website.theme if website and website.theme else 'halink-c5'
    return theme_key.strip()

def parse_theme_info(theme_key):
    functions_path = BASE_DIR / 'public_html' / 'halink-content' / 'themes' / theme_key / 'functions.php'
    theme_info = {
        'key_theme': theme_key,
        'title_theme': theme_key.replace('halink-', '').capitalize(),
        'type_theme': 'Giao diện website',
        'version_theme': '1.0',
        'author_theme': 'Halink',
        'screenshot_url': f'/static/halink-content/themes/{theme_key}/screenshot.png'
    }
    
    if os.path.exists(functions_path):
        try:
            with open(functions_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Phân tích hàm setup để lấy meta
            setup_match = re.search(r'function\s+setup\s*\(\s*\)\s*\{(.*?)\}', content, re.DOTALL)
            if setup_match:
                setup_body = setup_match.group(1)
                for key in ['key_theme', 'title_theme', 'type_theme', 'version_theme', 'author_theme']:
                    match = re.search(r"'" + key + r"'\s*=>\s*'([^']*)'", setup_body)
                    if match:
                        theme_info[key] = match.group(1)
        except Exception:
            pass
            
    # Kiểm tra screenshot thực tế
    screenshot_jpg = BASE_DIR / 'public_html' / 'halink-content' / 'themes' / theme_key / 'screenshot.jpg'
    if os.path.exists(screenshot_jpg):
        theme_info['screenshot_url'] = f'/static/halink-content/themes/{theme_key}/screenshot.jpg'
        
    return theme_info

def parse_sidebars_from_theme(theme_key):
    functions_path = BASE_DIR / 'public_html' / 'halink-content' / 'themes' / theme_key / 'functions.php'
    sidebars = []
    
    if os.path.exists(functions_path):
        try:
            with open(functions_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            setup_match = re.search(r'function\s+halink_widgets_setup\s*\(\s*\)\s*\{(.*?)\}', content, re.DOTALL)
            if setup_match:
                body = setup_match.group(1)
                # Tìm các array con
                arrays = re.findall(r'array\s*\((.*?)\)', body, re.DOTALL)
                if not arrays:
                    arrays = re.findall(r'\[(.*?)\]', body, re.DOTALL)
                    
                for arr in arrays:
                    name_m = re.search(r"'(?:name|title)'\s*=>\s*'([^']*)'", arr)
                    id_m = re.search(r"'id'\s*=>\s*'([^']*)'", arr)
                    if name_m and id_m:
                        sidebars.append({
                            'name': name_m.group(1),
                            'id': id_m.group(1)
                        })
        except Exception:
            pass
            
    # Fallback nếu không parse được hoặc rỗng
    if not sidebars:
        sidebars = [
            {'name': 'Banner header', 'id': 'halink_header_wg'},
            {'name': 'Banner trang sản phẩm', 'id': 'halink_header_product_wg'},
            {'name': 'Nội dung trang chủ', 'id': 'halink_home_wg'},
            {'name': 'Footer top', 'id': 'halink_footer0_wg'},
            {'name': 'Footer thanh toán', 'id': 'halink_footer3_wg'},
            {'name': 'Footer middle', 'id': 'halink_footer1_wg'},
            {'name': 'Footer bottom', 'id': 'halink_footer2_wg'},
            {'name': 'Tab giải thưởng', 'id': 'halink_tab1_wg'},
            {'name': 'Tab cảm nhận khách hàng', 'id': 'halink_tab2_wg'},
            {'name': 'Tab ưu đãi - sự kiện', 'id': 'halink_tab3_wg'},
            {'name': 'Tab hình ảnh - video', 'id': 'halink_tab4_wg'},
            {'name': 'Tab tin tức & thư viện - video', 'id': 'halink_tab5_wg'},
        ]
    return sidebars

@staff_member_required
def theme_info_view(request):
    theme_key = get_active_theme()
    theme_info = parse_theme_info(theme_key)
    context = {
        'theme_info': theme_info,
        'title': 'Giao diện & Cấu hình',
    }
    context.update(admin.site.each_context(request))
    return render(request, 'admin/theme_info.html', context)

@staff_member_required
def widgets_view(request):
    theme_key = get_active_theme()
    sidebars = parse_sidebars_from_theme(theme_key)
    
    # Lấy cấu hình các widget từ database
    widgets_meta = HalinkMeta.objects.filter(meta_type='widgets').first()
    sidebar_mapping = {}
    if widgets_meta and widgets_meta.meta_value:
        try:
            sidebar_mapping = json.loads(widgets_meta.meta_value)
        except Exception:
            pass
            
    # Lấy nội dung chi tiết của các widget đang lưu trong DB
    content_meta = HalinkMeta.objects.filter(meta_type='widget_content')
    widget_contents = {}
    for item in content_meta:
        if item.meta_title and item.meta_value:
            try:
                # Phân tích dữ liệu JSON thành dict
                fields_list = json.loads(item.meta_value)
                fields_dict = {}
                for f in fields_list:
                    fields_dict[f.get('name')] = f.get('value', '')
                widget_contents[item.meta_title] = fields_dict
            except Exception:
                pass
                
    # Chuẩn bị danh sách dropdown cho các Widget có chọn Menu hoặc Danh mục
    menus = [{'id': m.Id, 'title': clean_lang(m.title_cat)} for m in HalinkMenu.objects.all()]
    post_cats = [{'id': p.Id, 'title': clean_lang(p.title_vn)} for p in HalinkPost.objects.filter(post_type='postcat')]
    product_cats = [{'id': p.Id, 'title': clean_lang(p.title_vn)} for p in HalinkPost.objects.filter(post_type='productcat')]
    
    context = {
        'sidebars': sidebars,
        'available_widgets': AVAILABLE_WIDGETS,
        'menus': menus,
        'post_cats': post_cats,
        'product_cats': product_cats,
        'sidebar_mapping': sidebar_mapping,
        'widget_contents': widget_contents,
        'title': 'Quản lý Widgets',
    }
    context.update(admin.site.each_context(request))
    return render(request, 'admin/widgets.html', context)

@csrf_exempt
@staff_member_required
def widgets_save_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Chỉ chấp nhận phương thức POST'}, status=400)
        
    try:
        data = json.loads(request.body)
        sidebars_data = data.get('sidebars', {})  # Map: sidebar_id -> [widget_instance_id, ...]
        widget_contents = data.get('widget_data', {})  # Map: widget_instance_id -> {field_name: value}
        
        # Bắt đầu transaction để đảm bảo dữ liệu ghi xuống an toàn
        with transaction.atomic():
            # 1. Lưu cấu hình vị trí Widgets
            widgets_meta = HalinkMeta.objects.filter(meta_type='widgets').first()
            if not widgets_meta:
                widgets_meta = HalinkMeta(meta_type='widgets', ticlock=0)
                
            widgets_meta.meta_value = json.dumps(sidebars_data, ensure_ascii=False)
            widgets_meta.date = timezone.now()
            widgets_meta.save()
            
            # Thu thập tất cả các Widget ID đang hoạt động
            active_widget_ids = set()
            for w_list in sidebars_data.values():
                if isinstance(w_list, list):
                    for wid in w_list:
                        if wid:
                            active_widget_ids.add(wid)
                elif isinstance(w_list, str) and w_list:
                    # Hỗ trợ chuỗi comma-separated
                    for wid in w_list.split(','):
                        if wid.strip():
                            active_widget_ids.add(wid.strip())
                            
            # 2. Xóa các widget_content trong DB không còn được dùng nữa (để tránh rác DB)
            HalinkMeta.objects.filter(meta_type='widget_content').exclude(meta_title__in=active_widget_ids).delete()
            
            # 3. Cập nhật hoặc thêm mới nội dung từng Widget hoạt động
            for wid in active_widget_ids:
                w_fields = widget_contents.get(wid, {})
                
                # Định dạng dữ liệu của widget_content dưới dạng list các đối tượng name-value
                # Để lưu trữ chuẩn PHP, ta cần duyệt qua định nghĩa widget và tự động bọc thẻ đa ngôn ngữ
                # Tìm xem widget thuộc loại nào
                # Ví dụ ID: halink_widget_slider_id_wg_7___htransferl____1
                widget_type = None
                for key in AVAILABLE_WIDGETS.keys():
                    if wid.startswith(key):
                        widget_type = key
                        break
                        
                # Nếu không tìm thấy, fallback lấy mặc định hoặc bỏ qua bọc đa ngôn ngữ
                widget_def = AVAILABLE_WIDGETS.get(widget_type) if widget_type else None
                
                # Danh sách lưu trữ JSON
                saved_fields = []
                
                if widget_def:
                    for field in widget_def['fields']:
                        f_name = field['name']
                        is_multilang = field['multilang']
                        
                        if is_multilang:
                            # Với trường đa ngôn ngữ, hệ thống cũ mong đợi:
                            # 1. Trường gốc (e.g. title) chứa: [[[:vi]]]Tiêu đề vi[[[:end_vi]]][[[:en]]]Tiêu đề en[[[:end_en]]]
                            # 2. Trường {name}_lg_vi chứa: Tiêu đề vi
                            # 3. Trường {name}_lg_en chứa: Tiêu đề en
                            vi_val = w_fields.get(f"{f_name}_vi", "").strip()
                            en_val = w_fields.get(f"{f_name}_en", "").strip()
                            
                            wrapped_val = f"[[[:vi]]]{vi_val}[[[:end_vi]]][[[:en]]]{en_val}[[[:end_en]]]"
                            
                            saved_fields.append({"name": f_name, "value": wrapped_val})
                            saved_fields.append({"name": f"{f_name}_lg_vi", "value": vi_val})
                            saved_fields.append({"name": f"{f_name}_lg_en", "value": en_val})
                        else:
                            # Trường thường không có ngôn ngữ
                            val = w_fields.get(f_name, "")
                            saved_fields.append({"name": f_name, "value": str(val).strip()})
                            
                    # Thêm các trường ngoài định nghĩa nếu có gửi lên
                    for k, v in w_fields.items():
                        # Kiểm tra xem k có nằm trong danh sách đã lưu chưa
                        if not any(f['name'] == k or f['name'] == k.replace('_vi','').replace('_en','') for f in saved_fields):
                            saved_fields.append({"name": k, "value": str(v).strip()})
                else:
                    # Nếu widget không nằm trong danh sách có sẵn, lưu thô các cặp key-value
                    for k, v in w_fields.items():
                        saved_fields.append({"name": k, "value": str(v).strip()})
                        
                # Cập nhật hoặc lưu vào DB
                meta_item = HalinkMeta.objects.filter(meta_type='widget_content', meta_title=wid).first()
                if not meta_item:
                    meta_item = HalinkMeta(meta_type='widget_content', meta_title=wid, ticlock=0)
                    
                meta_item.meta_value = json.dumps(saved_fields, ensure_ascii=False)
                meta_item.date = timezone.now()
                meta_item.save()
                
        return JsonResponse({'status': 'success', 'message': 'Đã lưu cấu hình widgets thành công!'})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'status': 'error', 'message': f'Lỗi hệ thống: {str(e)}'}, status=500)
