from django import forms
import re
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
            vi_match = re.search(r'\\[\\[\\[:vi\\]\\]\\](.*?)\\[\\[\\[:end_vi\\]\\]\\]', value, re.DOTALL)
            en_match = re.search(r'\\[\\[\\[:en\\]\\]\\](.*?)\\[\\[\\[:end_en\\]\\]\\]', value, re.DOTALL)

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
    Widget hien thi danh sach chuyen muc dang checkbox co phan cap.
    Tu dong ho tro giao dien toi/sang (Dark/Light mode) dua tren class .dark cua Unfold.
    """

    def __init__(self, category_type='postcat', *args, **kwargs):
        self.category_type = category_type
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        from .models import HalinkPost

        categories = HalinkPost.objects.filter(
            post_type=self.category_type
        ).order_by('sort', 'Id')

        selected_ids = []
        if value:
            selected_ids = [v.strip() for v in str(value).strip(',').split(',') if v.strip()]

        rows = []
        for cat in categories:
            cat_id = str(cat.Id)
            checked = 'checked' if cat_id in selected_ids else ''

            raw_title = cat.title_vn or f'ID: {cat_id}'
            vi_match = re.search(r'\\[\\[\\[:vi\\]\\]\\](.*?)\\[\\[\\[:end_vi\\]\\]\\]', raw_title, re.DOTALL)
            title = vi_match.group(1).strip() if vi_match else re.sub(r'\\[\\[\\[:[^\\]]+\\]\\]\\]', '', raw_title).strip()

            indent = '&nbsp;&nbsp;&nbsp;— ' if cat.idcat else ''

            rows.append(
                f'<label class="cat-item">'
                f'<input type="checkbox" name="{name}" value="{cat_id}" {checked}>'
                f'<span>{indent}{title}</span>'
                f'</label>'
            )

        inner = '\n'.join(rows) if rows else '<p style="color:#888;font-size:13px;">Chua co chuyen muc nao.</p>'

        html = f'''<div class="category-checkbox-widget">
<style>
.category-checkbox-widget {{
    max-height: 220px; overflow-y: auto;
    border: 1px solid #e4e4e7; border-radius: 8px;
    padding: 8px 10px; background: #ffffff;
}}
.dark .category-checkbox-widget {{
    border-color: rgb(63 63 70); background: rgb(24 24 27);
}}
.category-checkbox-widget .cat-item {{
    display: flex; align-items: center; gap: 8px;
    padding: 4px 6px; border-radius: 4px; cursor: pointer;
    color: #18181b; font-size: 13px; transition: background 0.15s;
}}
.dark .category-checkbox-widget .cat-item {{
    color: rgb(228 228 231);
}}
.category-checkbox-widget .cat-item:hover {{ background: #f4f4f5; }}
.dark .category-checkbox-widget .cat-item:hover {{ background: rgb(39 39 42); }}
.category-checkbox-widget input[type="checkbox"] {{
    accent-color: #7c3aed; width: 15px; height: 15px; flex-shrink: 0;
}}
</style>
{inner}
</div>
<p style="font-size:11px; color:#6b7280; margin-top:4px;">Tick chon chuyen muc cho bai viet nay.</p>'''

        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        values = data.getlist(name)
        if values:
            return ','.join(values) + ','
        return ''


class ImagePickerWidget(forms.TextInput):
    """
    Widget cho field post_image: o nhap (ho tro dark mode) + preview + nut mo popup chon anh.
    Tu dong ho tro giao dien toi/sang cua Unfold.
    """
    def __init__(self, subfolder='hinhanh', *args, **kwargs):
        self.subfolder = subfolder
        attrs = kwargs.get('attrs', {}) or {}
        default_attrs = {
            'class': 'border border-gray-300 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-950 dark:text-zinc-200 rounded-lg p-2 w-full focus:ring-1 focus:ring-primary-500 focus:outline-none'
        }
        default_attrs.update(attrs)
        kwargs['attrs'] = default_attrs
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        from django.conf import settings
        field_id = (attrs or {}).get('id', f'id_{{name}}')
        browser_url = f'/admin/suoi_tien/image-browser/?field_id={{field_id}}&subfolder={{self.subfolder}}'

        preview_html = ''
        if value:
            img_url = f"{{settings.MEDIA_URL}}{{value}}"
            preview_html = (
                f'<div id="{{field_id}}_preview" style="margin-top:8px;">'
                f'<img src="{{img_url}}" style="max-height:120px;max-width:240px;'
                f'border-radius:8px;border:1px solid #e4e4e7;object-fit:cover;" '
                f'class="img-preview" onerror="this.style.display=\\'none\\'">'
                f'</div>'
            )
        else:
            preview_html = f'<div id="{{field_id}}_preview" style="margin-top:8px;"></div>'

        text_input = super().render(name, value, attrs, renderer)

        html = f"""
<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
  <div style="flex:1;min-width:200px;">{{text_input}}</div>
  <button type="button" class="image-picker-btn"
    onclick="openImageBrowser('{{field_id}}', '{{browser_url}}')">
    &#128247; Chọn ảnh
  </button>
</div>
{{preview_html}}
<style>
.image-picker-btn {{
    padding: 7px 14px; border-radius: 6px; font-size: 13px; cursor: pointer;
    display: flex; align-items: center; gap: 6px; white-space: nowrap; transition: all 0.15s;
    background: #f3e8ff; color: #6b21a8; border: 1px solid #c084fc;
}}
.image-picker-btn:hover {{ background: #e9d5ff; }}
.dark .image-picker-btn {{
    background: #1e1b4b; color: #a78bfa; border: 1px solid #7c3aed;
}}
.dark .image-picker-btn:hover {{ background: #312e81; }}
.dark .img-preview {{ border-color: rgb(63 63 70) !important; }}
</style>
<script>
if (!window._imgPickerReady) {{
  window._imgPickerReady = true;
  window.receiveImageFromBrowser = function(fieldId, path, name) {{
    var inp = document.getElementById(fieldId);
    if (inp) {{
      inp.value = path;
      inp.dispatchEvent(new Event('change'));
    }}
    var prev = document.getElementById(fieldId + '_preview');
    if (prev) {{
      prev.innerHTML = '<img src="/media/' + path + '" style="max-height:120px;max-width:240px;border-radius:8px;border:1px solid #e4e4e7;object-fit:cover;margin-top:8px;" class="img-preview">';
    }}
  }};
  window.openImageBrowser = function(fieldId, url) {{
    var w = 900, h = 600;
    var left = (screen.width - w) / 2;
    var top  = (screen.height - h) / 2;
    window.open(url, 'image_browser',
      'width=' + w + ',height=' + h + ',top=' + top + ',left=' + left + ',resizable=yes,scrollbars=yes');
  }};
}}
</script>"""
        return mark_safe(html)
