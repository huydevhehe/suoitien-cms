from django import forms
import re
import datetime
from django.utils.safestring import mark_safe


class MultiLangWidget(forms.MultiWidget):
    template_name = 'admin/widgets/multi_lang.html'

    def __init__(self, widget_class=forms.TextInput, attrs=None):
        default_attrs = {
            'class': 'border border-gray-300 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-950 dark:text-zinc-200 rounded-lg p-2 w-full focus:ring-1 focus:ring-primary-500 focus:outline-none'
        }
        if attrs:
            default_attrs.update(attrs)

        widgets = [
            widget_class(attrs=default_attrs),
            widget_class(attrs=default_attrs),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            vi_match = re.search(r'\[\[\[:vi\]\]\](.*?)\[\[\[:end_vi\]\]\]', value, re.DOTALL)
            en_match = re.search(r'\[\[\[:en\]\]\](.*?)\[\[\[:end_en\]\]\]', value, re.DOTALL)

            vi_val = vi_match.group(1).strip() if vi_match else ""
            en_val = en_match.group(1).strip() if en_match else ""

            if not vi_match and not en_match:
                vi_val = value.strip()
            return [vi_val, en_val]
        return ["", ""]

    def value_from_datadict(self, data, files, name):
        vi_val = data.get(f"{name}_0", "").strip()
        en_val = data.get(f"{name}_1", "").strip()

        if not vi_val and not en_val:
            return ""

        return f"[[[:vi]]]{vi_val}[[[:end_vi]]][[[:en]]]{en_val}[[[:end_en]]]"


class CategoryCheckboxWidget(forms.Widget):
    """
    Widget chọn chuyên mục dạng hộp sổ xuống (dropdown collapsible) chứa checkbox.
    Tự động cập nhật nhãn đã chọn và hỗ trợ giao diện tối/sáng của Unfold.
    """

    def __init__(self, category_type='postcat', exclude_id=None, *args, **kwargs):
        self.category_type = category_type
        self.exclude_id = exclude_id
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        from .models import HalinkPost

        qs = HalinkPost.objects.filter(post_type=self.category_type)
        if hasattr(self, 'exclude_id') and self.exclude_id:
            qs = qs.exclude(Id=self.exclude_id)
        categories = qs.order_by('sort', 'Id')

        selected_ids = []
        if value:
            selected_ids = [v.strip() for v in str(value).strip(',').split(',') if v.strip()]

        rows = []
        for cat in categories:
            cat_id = str(cat.Id)
            checked = 'checked' if cat_id in selected_ids else ''

            raw_title = cat.title_vn or f'ID: {cat_id}'
            vi_match = re.search(r'\[\[\[:vi\]\]\](.*?)\[\[\[:end_vi\]\]\]', raw_title, re.DOTALL)
            title = vi_match.group(1).strip() if vi_match else re.sub(r'\[\[\[:[^\]]+\]\]\]', '', raw_title).strip()

            indent = '&nbsp;&nbsp;&nbsp;— ' if cat.idcat else ''

            rows.append(
                '<label class="cat-item">'
                '<input type="checkbox" name="%s" value="%s" %s>'
                '<span>%s%s</span>'
                '</label>' % (name, cat_id, checked, indent, title)
            )

        inner = '\n'.join(rows) if rows else '<p style="color:#888;font-size:13px;padding:8px 12px;">Chưa có chuyên mục nào.</p>'

        html = """
<div class="category-dropdown-container" id="cat_container_%s">
  <div class="category-dropdown-header" onclick="toggleCategoryDropdown('cat_container_%s')">
    <span class="category-dropdown-selected-text">Chọn chuyên mục...</span>
    <span class="material-symbols-outlined dropdown-arrow">expand_more</span>
  </div>
  <div class="category-dropdown-panel">
    <div class="category-checkbox-widget">
      %s
    </div>
  </div>
</div>

<style>
.category-dropdown-container {
    position: relative;
    width: 100%%;
    max-width: 480px;
}
.category-dropdown-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    color: #1f2937;
    user-select: none;
    transition: all 0.15s;
}
.dark .category-dropdown-header {
    background: rgb(24 24 27);
    border-color: rgb(63 63 70);
    color: #f4f4f5;
}
.category-dropdown-header:hover {
    border-color: #9ca3af;
}
.dark .category-dropdown-header:hover {
    border-color: #52525b;
}
.category-dropdown-panel {
    display: none;
    position: absolute;
    top: 100%%;
    left: 0;
    width: 100%%;
    margin-top: 4px;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    z-index: 999;
}
.dark .category-dropdown-panel {
    background: rgb(24 24 27);
    border-color: rgb(63 63 70);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
}
.category-dropdown-container.open .category-dropdown-panel {
    display: block;
}
.category-dropdown-container.open .dropdown-arrow {
    transform: rotate(180deg);
}
.dropdown-arrow {
    transition: transform 0.2s;
    font-size: 18px;
    color: #6b7280;
}
.dark .dropdown-arrow {
    color: #a1a1aa;
}
.category-checkbox-widget {
    max-height: 220px;
    overflow-y: auto;
    padding: 8px 10px;
}
.category-checkbox-widget .cat-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 4px;
    cursor: pointer;
    color: #1f2937;
    font-size: 13px;
    transition: background 0.15s;
}
.dark .category-checkbox-widget .cat-item {
    color: #e5e7eb;
}
.category-checkbox-widget .cat-item:hover {
    background: #f3f4f6;
}
.dark .category-checkbox-widget .cat-item:hover {
    background: #27272a;
}
.category-checkbox-widget input[type="checkbox"] {
    accent-color: #7c3aed;
    width: 16px;
    height: 16px;
    flex-shrink: 0;
}
</style>

<script>
if (!window._categoryDropdownReady) {
  window._categoryDropdownReady = true;
  
  window.toggleCategoryDropdown = function(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const isOpen = container.classList.contains('open');
    
    // Close other dropdowns
    document.querySelectorAll('.category-dropdown-container').forEach(c => {
      c.classList.remove('open');
    });
    
    if (!isOpen) {
      container.classList.add('open');
    }
  };

  // Click outside to close
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.category-dropdown-container')) {
      document.querySelectorAll('.category-dropdown-container').forEach(c => {
        c.classList.remove('open');
      });
    }
  });

  // Update dropdown text based on checkbox status
  window.updateCategorySelectedText = function(container) {
    const checkedBoxes = container.querySelectorAll('input[type="checkbox"]:checked');
    const textSpan = container.querySelector('.category-dropdown-selected-text');
    if (!textSpan) return;
    
    if (checkedBoxes.length === 0) {
      textSpan.textContent = 'Chọn chuyên mục...';
      textSpan.style.color = '';
    } else {
      const names = [];
      checkedBoxes.forEach(cb => {
        let labelText = cb.nextElementSibling.textContent;
        labelText = labelText.replace(/^[\\s —-]+/, '');
        names.push(labelText);
      });
      textSpan.textContent = names.join(', ');
      textSpan.style.color = '#a78bfa'; // Violet tone matching dark/light mode
    }
  };

  // Bind event
  document.addEventListener('change', function(e) {
    if (e.target.matches('.category-checkbox-widget input[type="checkbox"]')) {
      const container = e.target.closest('.category-dropdown-container');
      if (container) {
        window.updateCategorySelectedText(container);
      }
    }
  });
}

// Perform initial setup for this container
(function() {
  const container = document.getElementById('cat_container_%s');
  if (container) {
    window.updateCategorySelectedText(container);
  }
})();
</script>
""" % (name, name, inner, name)

        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        values = data.getlist(name)
        if values:
            return ','.join(values) + ','
        return ''


class ImagePickerWidget(forms.TextInput):
    """
    Widget cho field post_image: ô nhập (hỗ trợ dark mode) + preview + nút mở popup chọn ảnh.
    Tự động hỗ trợ giao diện tối/sáng của Unfold.
    """
    def __init__(self, subfolder='hinhanh', *args, **kwargs):
        self.subfolder = subfolder
        attrs = kwargs.get('attrs', {}) or {}
        # Dùng class riêng để CSS override bên dưới bắt chính xác
        default_attrs = {
            'class': 'image-picker-input rounded-lg p-2 w-full focus:ring-1 focus:ring-primary-500 focus:outline-none'
        }
        default_attrs.update(attrs)
        kwargs['attrs'] = default_attrs
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        from django.conf import settings
        field_id = (attrs or {}).get('id', 'id_%s' % name)
        browser_url = '/admin/suoi_tien/image-browser/?field_id=%s&subfolder=%s' % (field_id, self.subfolder)

        # Preview ảnh nếu có giá trị
        preview_html = ''
        if value:
            img_url = '%s%s' % (settings.MEDIA_URL, value)
            preview_html = (
                '<div id="%s_preview" style="margin-top:8px;">'
                '<img src="%s" style="max-height:120px;max-width:240px;'
                'border-radius:8px;border:1px solid #e4e4e7;object-fit:cover;" '
                'class="img-preview" onerror="this.remove()">'
                '</div>'
            ) % (field_id, img_url)
        else:
            preview_html = '<div id="%s_preview" style="margin-top:8px;"></div>' % field_id

        text_input = super().render(name, value, attrs, renderer)

        html = """
<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
  <div style="flex:1;min-width:200px;">%s</div>
  <button type="button" class="image-picker-btn"
    onclick="openImageBrowser('%s', '%s')">
    &#128247; Chọn ảnh
  </button>
</div>
%s
<style>
/* CSS cho ô nhập text của ImagePicker */
.image-picker-input {
    background-color: #ffffff !important;
    color: #1f2937 !important;
    border: 1px solid #d1d5db !important;
}
.dark .image-picker-input {
    background-color: rgb(24 24 27) !important;
    color: #f4f4f5 !important;
    border-color: rgb(63 63 70) !important;
}

/* CSS cho nút Chọn ảnh */
.image-picker-btn {
    padding: 7px 14px; border-radius: 6px; font-size: 13px; cursor: pointer;
    display: flex; align-items: center; gap: 6px; white-space: nowrap; transition: all 0.15s;
    background: #f3e8ff; color: #6b21a8; border: 1px solid #c084fc;
}
.image-picker-btn:hover { background: #e9d5ff; }
.dark .image-picker-btn {
    background: #1e1b4b; color: #a78bfa; border: 1px solid #7c3aed;
}
.dark .image-picker-btn:hover { background: #312e81; }
.dark .img-preview { border-color: rgb(63 63 70) !important; }
</style>
<script>
if (!window._imgPickerReady) {
  window._imgPickerReady = true;
  window.receiveImageFromBrowser = function(fieldId, path, name) {
    var inp = document.getElementById(fieldId);
    if (inp) {
      inp.value = path;
      inp.dispatchEvent(new Event('change'));
    }
    var prev = document.getElementById(fieldId + '_preview');
    if (prev) {
      prev.innerHTML = '<img src="/media/' + path + '" style="max-height:120px;max-width:240px;border-radius:8px;border:1px solid #e4e4e7;object-fit:cover;margin-top:8px;" class="img-preview" onerror="this.remove()">';
    }
  };
  window.openImageBrowser = function(fieldId, url) {
    var w = 900, h = 600;
    var left = (screen.width - w) / 2;
    var top  = (screen.height - h) / 2;
    window.open(url, 'image_browser',
      'width=' + w + ',height=' + h + ',top=' + top + ',left=' + left + ',resizable=yes,scrollbars=yes');
  };
}
</script>""" % (text_input, field_id, browser_url, preview_html)
        return mark_safe(html)


class SidebarCheckboxWidget(forms.Widget):
    """
    Widget hiển thị danh sách các Sidebar dưới dạng check-box.
    Tự động đọc cấu hình sidebar từ theme hiện tại.
    """
    def render(self, name, value, attrs=None, renderer=None):
        from .views import parse_sidebars_from_theme, get_active_theme
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


from unfold.widgets import UnfoldBooleanSwitchWidget
import datetime

class StatusSwitchWidget(UnfoldBooleanSwitchWidget):
    """
    Switch Widget cho các trường lưu trạng thái dạng 0/1 hoặc '0'/'1' trong DB.
    Tự động chuyển đổi sang Boolean khi hiển thị và ngược lại khi lưu.
    """
    def __init__(self, is_char=False, attrs=None):
        self.is_char = is_char
        super().__init__(attrs)
        # Ghi đè check_test vì UnfoldBooleanSwitchWidget mặc định ép None cho CheckboxInput
        self.check_test = lambda v: str(v) in ('1', 'True', 'true')

    def value_from_datadict(self, data, files, name):
        val = super().value_from_datadict(data, files, name)
        if val:
            return '1' if self.is_char else 1
        else:
            return '0' if self.is_char else 0


class UnixTimestampDateTimeWidget(forms.DateTimeInput):
    """
    Widget chọn ngày giờ (datetime-local) cho trường lưu Unix Timestamp dạng số trong DB.
    Tự động chuyển đổi Timestamp thành định dạng hiển thị và ngược lại.
    """
    input_type = 'datetime-local'

    def __init__(self, attrs=None, format=None):
        default_attrs = {
            'class': 'border border-gray-300 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-950 dark:text-zinc-200 rounded-lg p-2 w-full focus:ring-1 focus:ring-primary-500 focus:outline-none'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format=format)

    def format_value(self, value):
        if value:
            try:
                dt = datetime.datetime.fromtimestamp(int(value))
                return dt.strftime('%Y-%m-%dT%H:%M')
            except (ValueError, TypeError):
                pass
        return value

    def value_from_datadict(self, data, files, name):
        val = data.get(name, None)
        if val:
            try:
                if 'T' in val:
                    dt = datetime.datetime.strptime(val, '%Y-%m-%dT%H:%M')
                else:
                    dt = datetime.datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
                return int(dt.timestamp())
            except ValueError:
                try:
                    dt = datetime.datetime.strptime(val, '%Y-%m-%dT%H:%M:%S')
                    return int(dt.timestamp())
                except Exception:
                    pass
        return val


import json

class JSONTextAreaWidget(forms.Textarea):
    """
    Widget hiển thị và tự động định dạng đẹp (beautify) dữ liệu JSON trong Textarea.
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'font-mono text-xs border border-gray-300 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-950 dark:text-zinc-200 rounded-lg p-2 w-full focus:ring-1 focus:ring-primary-500 focus:outline-none',
            'style': 'font-family: monospace; font-size: 13px;',
            'rows': 10,
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def format_value(self, value):
        if value:
            try:
                # Đọc chuỗi JSON và định dạng lại có thụt lề
                obj = json.loads(value)
                return json.dumps(obj, indent=2, ensure_ascii=False)
            except Exception:
                pass
        return value



