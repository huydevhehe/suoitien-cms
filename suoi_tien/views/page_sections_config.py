from suoi_tien.views.home_sections_config import HOME_SECTIONS

ABOUT_SECTIONS = {
    'section_1_banner': {
        'name': 'Tầng 1 - Banner Suối Tiên Story',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề chính (Ví dụ: SUỐI TIÊN, THEME PARK STORY)', 'type': 'wysiwyg', 'multilang': True},
            {'name': 'subtitle', 'label': 'Tiêu đề phụ (Hành trình 30 năm kiến tạo...)', 'type': 'wysiwyg', 'multilang': True},
            {'name': 'description', 'label': 'Đoạn mô tả (Nơi hội tụ văn hóa...)', 'type': 'wysiwyg', 'multilang': True},
            {'name': 'images', 'label': 'Danh sách ảnh nền (thêm nhiều ảnh làm slider)', 'type': 'image_list', 'multilang': False},
        ],
    },
    'section_2_hello_stats': {
        'name': 'Tầng 2 - Xin Chào & Thống Kê',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề (Xin Chào)', 'type': 'wysiwyg', 'multilang': True},
            {'name': 'subtitle', 'label': 'Tiêu đề phụ (Khám phá Suối Tiên trong một cái nhìn)', 'type': 'wysiwyg', 'multilang': True},
            {'name': 'stat_1_num', 'label': 'Thống kê 1 - Chữ số (VD: 30+)', 'type': 'text', 'multilang': False},
            {'name': 'stat_1_label', 'label': 'Thống kê 1 - Nhãn (VD: Năm Phát Triển)', 'type': 'text', 'multilang': True},
            {'name': 'stat_2_num', 'label': 'Thống kê 2 - Chữ số (VD: 55Ha)', 'type': 'text', 'multilang': False},
            {'name': 'stat_2_label', 'label': 'Thống kê 2 - Nhãn (VD: Quy mô)', 'type': 'text', 'multilang': True},
            {'name': 'stat_3_num', 'label': 'Thống kê 3 - Chữ số (VD: 150+)', 'type': 'text', 'multilang': False},
            {'name': 'stat_3_label', 'label': 'Thống kê 3 - Nhãn (VD: Công Trình)', 'type': 'text', 'multilang': True},
            {'name': 'images', 'label': 'Danh sách ảnh slider quạt', 'type': 'image_list', 'multilang': False},
            {'name': 'bottom_text_1', 'label': 'Chữ chú thích dưới cùng 1', 'type': 'text', 'multilang': True},
            {'name': 'bottom_text_2', 'label': 'Chữ chú thích dưới cùng 2', 'type': 'text', 'multilang': True},
            {'name': 'bottom_text_3', 'label': 'Chữ chú thích dưới cùng 3', 'type': 'text', 'multilang': True},
        ],
    },
    'section_3_cards': {
        'name': 'Tầng 3 - Hành trình trải nghiệm (4 Thẻ)',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề khối (Không chỉ là khu vui chơi...)', 'type': 'textarea', 'multilang': True},
            # Thẻ 1
            {'name': 'card1_img', 'label': '[Thẻ 1] Hình ảnh', 'type': 'image', 'multilang': False},
            {'name': 'card1_title', 'label': '[Thẻ 1] Tên', 'type': 'text', 'multilang': True},
            {'name': 'card1_desc', 'label': '[Thẻ 1] Mô tả ngắn', 'type': 'textarea', 'multilang': True},
            {'name': 'card1_link', 'label': '[Thẻ 1] Link thủ công (Nếu không chọn bài viết)', 'type': 'text', 'multilang': False},
            {'name': 'card1_post_id', 'label': '[Thẻ 1] Chọn bài viết liên kết', 'type': 'select_post', 'multilang': False},
            # Thẻ 2
            {'name': 'card2_img', 'label': '[Thẻ 2] Hình ảnh', 'type': 'image', 'multilang': False},
            {'name': 'card2_title', 'label': '[Thẻ 2] Tên', 'type': 'text', 'multilang': True},
            {'name': 'card2_desc', 'label': '[Thẻ 2] Mô tả ngắn', 'type': 'textarea', 'multilang': True},
            {'name': 'card2_link', 'label': '[Thẻ 2] Link thủ công (Nếu không chọn bài viết)', 'type': 'text', 'multilang': False},
            {'name': 'card2_post_id', 'label': '[Thẻ 2] Chọn bài viết liên kết', 'type': 'select_post', 'multilang': False},
            # Thẻ 3
            {'name': 'card3_img', 'label': '[Thẻ 3] Hình ảnh', 'type': 'image', 'multilang': False},
            {'name': 'card3_title', 'label': '[Thẻ 3] Tên', 'type': 'text', 'multilang': True},
            {'name': 'card3_desc', 'label': '[Thẻ 3] Mô tả ngắn', 'type': 'textarea', 'multilang': True},
            {'name': 'card3_link', 'label': '[Thẻ 3] Link thủ công (Nếu không chọn bài viết)', 'type': 'text', 'multilang': False},
            {'name': 'card3_post_id', 'label': '[Thẻ 3] Chọn bài viết liên kết', 'type': 'select_post', 'multilang': False},
            # Thẻ 4
            {'name': 'card4_img', 'label': '[Thẻ 4] Hình ảnh', 'type': 'image', 'multilang': False},
            {'name': 'card4_title', 'label': '[Thẻ 4] Tên', 'type': 'text', 'multilang': True},
            {'name': 'card4_desc', 'label': '[Thẻ 4] Mô tả ngắn', 'type': 'textarea', 'multilang': True},
            {'name': 'card4_link', 'label': '[Thẻ 4] Link thủ công (Nếu không chọn bài viết)', 'type': 'text', 'multilang': False},
            {'name': 'card4_post_id', 'label': '[Thẻ 4] Chọn bài viết liên kết', 'type': 'select_post', 'multilang': False},
        ],
    },
}

TRAI_NGHIEM_SECTIONS = {
    'section_1_hero': {
        'name': 'Tầng 1 - Banner Hero',
        'group': 'C',
        'fields': [
            {'name': 'bg_image', 'label': 'Ảnh nền banner', 'type': 'image', 'multilang': False},
            {'name': 'title', 'label': 'Tiêu đề chính (VD: TRẢI NGHIỆM ĐẶC BIỆT)', 'type': 'text', 'multilang': True},
            {'name': 'subtitle', 'label': 'Tiêu đề phụ (VD: SPECIAL EXPERIENCES)', 'type': 'text', 'multilang': True},
        ],
    },
    'section_2_intro': {
        'name': 'Tầng 2 - Xin Chào & Dải Ảnh',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề (VD: Xin Chào)', 'type': 'text', 'multilang': True},
            {'name': 'subtitle', 'label': 'Tiêu đề phụ (VD: Khám phá Suối Tiên trong một cái nhìn)', 'type': 'text', 'multilang': True},
            {'name': 'image_strip', 'label': 'Dải ảnh ngang (chọn nhiều ảnh)', 'type': 'image_list', 'multilang': False},
            {'name': 'tabs', 'label': 'Các nút tab/lọc (chọn bài viết, FE tự lấy link)', 'type': 'post_list', 'multilang': False},
        ],
    },
    'section_3_features': {
        'name': 'Tầng 3 - Danh Sách Trải Nghiệm (5 thẻ)',
        'group': 'C',
        'fields': [
            # Thẻ 1
            {'name': 'card1_img', 'label': '[Thẻ 1] Ảnh', 'type': 'image', 'multilang': False},
            {'name': 'card1_title', 'label': '[Thẻ 1] Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'card1_desc', 'label': '[Thẻ 1] Mô tả', 'type': 'textarea', 'multilang': True},
            {'name': 'card1_post_id', 'label': '[Thẻ 1] Bài viết liên kết (nút "Tìm hiểu thêm")', 'type': 'select_post', 'multilang': False},
            # Thẻ 2
            {'name': 'card2_img', 'label': '[Thẻ 2] Ảnh', 'type': 'image', 'multilang': False},
            {'name': 'card2_title', 'label': '[Thẻ 2] Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'card2_desc', 'label': '[Thẻ 2] Mô tả', 'type': 'textarea', 'multilang': True},
            {'name': 'card2_post_id', 'label': '[Thẻ 2] Bài viết liên kết (nút "Tìm hiểu thêm")', 'type': 'select_post', 'multilang': False},
            # Thẻ 3
            {'name': 'card3_img', 'label': '[Thẻ 3] Ảnh', 'type': 'image', 'multilang': False},
            {'name': 'card3_title', 'label': '[Thẻ 3] Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'card3_desc', 'label': '[Thẻ 3] Mô tả', 'type': 'textarea', 'multilang': True},
            {'name': 'card3_post_id', 'label': '[Thẻ 3] Bài viết liên kết (nút "Tìm hiểu thêm")', 'type': 'select_post', 'multilang': False},
            # Thẻ 4
            {'name': 'card4_img', 'label': '[Thẻ 4] Ảnh', 'type': 'image', 'multilang': False},
            {'name': 'card4_title', 'label': '[Thẻ 4] Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'card4_desc', 'label': '[Thẻ 4] Mô tả', 'type': 'textarea', 'multilang': True},
            {'name': 'card4_post_id', 'label': '[Thẻ 4] Bài viết liên kết (nút "Tìm hiểu thêm")', 'type': 'select_post', 'multilang': False},
            # Thẻ 5
            {'name': 'card5_img', 'label': '[Thẻ 5] Ảnh', 'type': 'image', 'multilang': False},
            {'name': 'card5_title', 'label': '[Thẻ 5] Tiêu đề', 'type': 'text', 'multilang': True},
            {'name': 'card5_desc', 'label': '[Thẻ 5] Mô tả', 'type': 'textarea', 'multilang': True},
            {'name': 'card5_post_id', 'label': '[Thẻ 5] Bài viết liên kết (nút "Tìm hiểu thêm")', 'type': 'select_post', 'multilang': False},
        ],
    },
}

TROCOI_SECTIONS = {
    'section_1_hero': {
        'name': 'Tầng 1 - Banner Hero',
        'group': 'C',
        'fields': [
            {'name': 'bg_images', 'label': 'Ảnh nền banner (nhiều ảnh làm slider)', 'type': 'image_list', 'multilang': False},
            {'name': 'title', 'label': 'Tiêu đề chính (VD: TRẢI NGHIỆM TRÒ CHƠI TẠI SUỐI TIÊN)', 'type': 'text', 'multilang': True},
            {'name': 'subtitle', 'label': 'Tiêu đề phụ / chú thích dưới', 'type': 'text', 'multilang': True},
        ],
    },
    'section_2_game_grid': {
        'name': 'Tầng 2 - Lưới Trò Chơi Theo Chuyên Mục',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề tầng (VD: Khám Phá Các Trò Chơi)', 'type': 'text', 'multilang': True},
            {'name': 'categories', 'label': 'Danh sách chuyên mục hiển thị (chọn từng chuyên mục)', 'type': 'cat_list', 'multilang': False},
            {'name': 'limit_cats', 'label': 'Hiển thị tối đa bao nhiêu chuyên mục (để trống = không giới hạn)', 'type': 'text', 'multilang': False},
            {'name': 'limit_per_cat', 'label': 'Mỗi chuyên mục hiển thị tối đa bao nhiêu bài (để trống = không giới hạn)', 'type': 'text', 'multilang': False},
        ],
    },
}

DICH_VU_SECTIONS = {
    'section_1_hero': {
        'name': 'Tầng 1 - Banner Hero',
        'group': 'C',
        'fields': [
            {'name': 'bg_images', 'label': 'Ảnh nền banner (nhiều ảnh, làm slider quạt)', 'type': 'image_list', 'multilang': False},
            {'name': 'title', 'label': 'Tiêu đề chính (VD: ĐA DẠNG DỊCH VỤ)', 'type': 'text', 'multilang': True},
            {'name': 'subtitle', 'label': 'Tiêu đề phụ (VD: DÀNH CHO TỔ CHỨC VÀ CÁ NHÂN)', 'type': 'text', 'multilang': True},
            {'name': 'description', 'label': 'Mô tả nhỏ phía dưới (VD: DIVERSE SERVICE PACKAGES...)', 'type': 'text', 'multilang': True},
        ],
    },
    'section_2_service_tags': {
        'name': 'Tầng 2 - Tag Dịch Vụ',
        'group': 'C',
        'fields': [
            {'name': 'tabs', 'label': 'Danh sách tag dịch vụ (tên hiển thị + bài viết liên kết)', 'type': 'post_list', 'multilang': False},
        ],
    },
    'section_3_cooperation': {
        'name': 'Tầng 3 - Loại Hình Hợp Tác',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Nhãn nút hợp tác (VD: LOẠI HÌNH HỢP TÁC)', 'type': 'text', 'multilang': True},
            {'name': 'zalo_phone', 'label': 'Số Zalo (VD: 0901234567) — FE tự build link zalo.me/...', 'type': 'text', 'multilang': False},
            {'name': 'call_phone', 'label': 'Số Gọi Ngay (VD: 0901234567) — FE tự build tel:...', 'type': 'text', 'multilang': False},
        ],
    },
}

DICH_VU_HOI_NGHI_SECTIONS = {
    'section_1_hero': {
        'name': 'Tầng 1 - Banner Hero',
        'group': 'C',
        'fields': [
            {'name': 'bg_images', 'label': 'Ảnh nền banner (nhiều ảnh, làm slider)', 'type': 'image_list', 'multilang': False},
            {'name': 'title', 'label': 'Tiêu đề nhỏ phía trên (VD: DỊCH VỤ)', 'type': 'text', 'multilang': True},
            {'name': 'subtitle', 'label': 'Tiêu đề lớn (VD: TỔ CHỨC HỘI NGHỊ TẠI SUỐI TIÊN)', 'type': 'text', 'multilang': True},
        ],
    },
    'section_2_articles': {
        'name': 'Tầng 2 - Bài Viết Hội Nghị (6 thẻ)',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề tầng (VD: TỔ CHỨC HỘI NGHỊ TẠI SUỐI TIÊN)', 'type': 'text', 'multilang': True},
            {'name': 'posts', 'label': 'Danh sách bài viết (tối đa 6 bài, lấy ảnh + tiêu đề từ bài)', 'type': 'post_list', 'multilang': False, 'max': 6},
        ],
    },
}

TIN_TUC_SECTIONS = {
    'section_1_hero': {
        'name': 'Tầng 1 - Banner Hero',
        'group': 'C',
        'fields': [
            {'name': 'bg_image', 'label': 'Ảnh nền banner', 'type': 'image', 'multilang': False},
            {'name': 'title', 'label': 'Tiêu đề (VD: TIN TỨC)', 'type': 'text', 'multilang': True},
        ],
    },
    'section_2_news_grid': {
        'name': 'Tầng 2 - Lưới Tin Tức Theo Chuyên Mục',
        'group': 'C',
        'fields': [
            {'name': 'categories', 'label': 'Danh sách chuyên mục hiển thị trong dropdown (chọn từng chuyên mục)', 'type': 'cat_list', 'multilang': False},
            {'name': 'limit_cats', 'label': 'Số chuyên mục tối đa trong dropdown (để trống = không giới hạn)', 'type': 'text', 'multilang': False},
            {'name': 'limit_per_cat', 'label': 'Tổng bài lấy về mỗi chuyên mục (VD: 8)', 'type': 'text', 'multilang': False},
            {'name': 'limit_per_page', 'label': 'Số bài hiển thị mỗi trang — FE dùng để chia trang (VD: 4)', 'type': 'text', 'multilang': False},
        ],
    },
}

CHINH_SACH_TOUR_DOAN_SECTIONS = {
    'section_1_articles': {
        'name': 'Tầng 1 - Tiêu Đề & Bài Viết Tour Đoàn',
        'group': 'C',
        'fields': [
            {'name': 'title', 'label': 'Tiêu đề chính (VD: CHÍNH SÁCH TOUR ĐOÀN)', 'type': 'text', 'multilang': True},
            {'name': 'subtitle', 'label': 'Tiêu đề phụ (VD: SUOI TIEN THEME PARK COMBO PACKAGES)', 'type': 'text', 'multilang': True},
            {'name': 'posts', 'label': 'Danh sách bài viết (tối đa 6 bài, lấy ảnh + tiêu đề từ bài)', 'type': 'post_list', 'multilang': False, 'max': 6},
        ],
    },
}

PAGES = {
    'home': {
        'name': 'Trang Chủ',
        'sections': HOME_SECTIONS
    },
    'gioi-thieu': {
        'name': 'Giới Thiệu (About)',
        'sections': ABOUT_SECTIONS
    },
    'trai-nghiem': {
        'name': 'Trải Nghiệm',
        'sections': TRAI_NGHIEM_SECTIONS
    },
    'tro-choi': {
        'name': 'Trò Chơi',
        'sections': TROCOI_SECTIONS
    },
    'dich-vu': {
        'name': 'Dịch Vụ',
        'sections': DICH_VU_SECTIONS
    },
    'dich-vu-hoi-nghi': {
        'name': 'Dịch Vụ - Hội Nghị',
        'sections': DICH_VU_HOI_NGHI_SECTIONS
    },
    'chinh-sach-tour-doan': {
        'name': 'Chính Sách Tour Đoàn',
        'sections': CHINH_SACH_TOUR_DOAN_SECTIONS
    },
    'tin-tuc': {
        'name': 'Tin Tức',
        'sections': TIN_TUC_SECTIONS
    },
}
