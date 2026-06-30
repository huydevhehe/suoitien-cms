from django import forms
from django.utils.safestring import mark_safe


class SidebarCheckboxWidget(forms.Widget):
    """
    Widget hiển thị danh sách các Sidebar dưới dạng check-box.
    Tự động đọc cấu hình sidebar từ theme hiện tại.
    """
    template_name = 'django/forms/widgets/input.html'  # Unfold yêu cầu attribute này

    def render(self, name, value, attrs=None, renderer=None):
        from ..views import parse_sidebars_from_theme, get_active_theme
        import json

        try:
            theme_key = get_active_theme()
            sidebars = parse_sidebars_from_theme(theme_key)
        except Exception:
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

        selected_ids = []
        if value:
            # Hỗ trợ cả JSON string và danh sách phân tách dấu phẩy
            if str(value).startswith('['):
                try:
                    selected_ids = json.loads(value)
                except Exception:
                    pass
            if not selected_ids:
                selected_ids = [v.strip() for v in str(value).split(',') if v.strip()]

        rows = []
        for sb in sidebars:
            sb_id = sb['id']
            sb_name = sb['name']
            checked = 'checked' if sb_id in selected_ids else ''
            rows.append(
                '<label class="sidebar-item">'
                '<input type="checkbox" name="%s" value="%s" %s>'
                '<span>%s</span>'
                '</label>' % (name, sb_id, checked, sb_name)
            )

        inner = '\n'.join(rows)

        html = """
<div class="sidebar-checkbox-widget">
  %s
</div>
<style>
.sidebar-checkbox-widget {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 10px 14px;
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    max-height: 200px;
    overflow-y: auto;
}
.dark .sidebar-checkbox-widget {
    background: rgb(24 24 27);
    border-color: rgb(63 63 70);
}
.sidebar-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #1f2937;
    cursor: pointer;
    transition: color 0.15s;
    user-select: none;
}
.dark .sidebar-item {
    color: #e5e7eb;
}
.sidebar-item input[type="checkbox"] {
    accent-color: #7c3aed;
    width: 16px;
    height: 16px;
    cursor: pointer;
}
</style>
""" % inner
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        import json
        values = data.getlist(name)
        if values:
            return json.dumps(values)
        return ''
