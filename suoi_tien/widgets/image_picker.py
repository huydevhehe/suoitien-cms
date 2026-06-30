from django import forms
from django.utils.safestring import mark_safe


class PriceInputWidget(forms.NumberInput):
    """NumberInput với dark mode đúng — dùng inline CSS thay vì Tailwind (tránh bị purge)."""

    def render(self, name, value, attrs=None, renderer=None):
        attrs = dict(attrs or {})
        attrs['class'] = 'price-input rounded-md px-3 py-2 w-full sm:text-sm font-medium'
        html = super().render(name, value, attrs, renderer)
        style = (
            '<style>'
            '.price-input{background:#fff;color:#111827;border:1px solid #d1d5db;display:block;}'
            '.dark .price-input{background:rgb(24 24 27);color:#f4f4f5;border-color:rgb(63 63 70);}'
            '.price-input:focus{outline:none;box-shadow:0 0 0 2px #a855f7;border-color:#a855f7;}'
            '</style>'
        )
        return mark_safe(style + html)


class GalleryPickerWidget(forms.HiddenInput):
    """Multi-image picker: hiện thumbnails có nút ×, nút Thêm ảnh mở popup image browser."""

    def __init__(self, subfolder='hinhanh', *args, **kwargs):
        self.subfolder = subfolder
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        from django.conf import settings
        field_id = (attrs or {}).get('id', f'id_{name}')
        browser_url = f'/admin/suoi_tien/image-browser/?field_id={field_id}&subfolder={self.subfolder}'
        hidden_input = super().render(name, value, attrs, renderer)

        paths = [p.strip() for p in (value or '').split(',') if p.strip()]
        thumb_parts = []
        for path in paths:
            img_url = f'{settings.MEDIA_URL}{path}'
            thumb_parts.append(
                f'<div class="gallery-item" data-path="{path}" data-field="{field_id}" '
                f'style="position:relative;display:inline-block;margin:4px;">'
                f'<img src="{img_url}" style="width:80px;height:80px;object-fit:cover;'
                f'border-radius:6px;border:1px solid #d1d5db;" '
                f'onerror="this.closest(\'.gallery-item\').remove()">'
                f'<button type="button" class="gal-remove-btn" '
                f'style="position:absolute;top:-6px;right:-6px;background:#ef4444;color:#fff;'
                f'border:none;border-radius:50%;width:20px;height:20px;font-size:14px;'
                f'cursor:pointer;line-height:1;">×</button>'
                f'</div>'
            )
        thumb_html = ''.join(thumb_parts)

        html = f'''<div style="margin-bottom:8px;">
  <div id="{field_id}_list" style="display:flex;flex-wrap:wrap;gap:4px;min-height:20px;margin-bottom:8px;">{thumb_html}</div>
  <button type="button" onclick="galOpen('{field_id}','{browser_url}')" class="gallery-add-btn">＋ Thêm ảnh</button>
</div>
{hidden_input}
<style>
.gallery-add-btn{{padding:6px 14px;border-radius:6px;font-size:13px;cursor:pointer;background:#f3e8ff;color:#6b21a8;border:1px solid #c084fc;}}
.gallery-add-btn:hover{{background:#e9d5ff;}}
.dark .gallery-add-btn{{background:#1e1b4b;color:#a78bfa;border-color:#7c3aed;}}
.dark .gallery-add-btn:hover{{background:#312e81;}}
.dark .gallery-item img{{border-color:rgb(63 63 70)!important;}}
</style>
<script>
if (!window._galPickerReady) {{
  window._galPickerReady = true;
  window._galReg = {{}};

  if (!window.openImageBrowser) {{
    window.openImageBrowser = function(fieldId, url) {{
      var w=900,h=600,left=(screen.width-w)/2,top=(screen.height-h)/2;
      window.open(url,'image_browser','width='+w+',height='+h+',top='+top+',left='+left+',resizable=yes,scrollbars=yes');
    }};
  }}

  var _origRecv = window.receiveImageFromBrowser || function(){{}};
  window.receiveImageFromBrowser = function(fieldId, path, name) {{
    if (window._galReg[fieldId]) {{ window._galReg[fieldId](path); }}
    else {{ _origRecv(fieldId, path, name); }}
  }};

  window.galOpen = function(fieldId, url) {{ window.openImageBrowser(fieldId, url); }};

  window.galAdd = function(fieldId, path) {{
    var hidden = document.getElementById(fieldId);
    var list = document.getElementById(fieldId + '_list');
    if (!hidden || !list) return;
    var parts = hidden.value ? hidden.value.split(',').map(function(s){{return s.trim();}}).filter(Boolean) : [];
    if (parts.indexOf(path) >= 0) return;
    parts.push(path);
    hidden.value = parts.join(',');
    var div = document.createElement('div');
    div.className = 'gallery-item';
    div.dataset.path = path;
    div.dataset.field = fieldId;
    div.style.cssText = 'position:relative;display:inline-block;margin:4px;';
    var img = document.createElement('img');
    img.src = '/media/' + path;
    img.style.cssText = 'width:80px;height:80px;object-fit:cover;border-radius:6px;border:1px solid #d1d5db;';
    img.onerror = function() {{ div.remove(); }};
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = '×';
    btn.className = 'gal-remove-btn';
    btn.style.cssText = 'position:absolute;top:-6px;right:-6px;background:#ef4444;color:#fff;border:none;border-radius:50%;width:20px;height:20px;font-size:14px;cursor:pointer;line-height:1;';
    div.appendChild(img);
    div.appendChild(btn);
    list.appendChild(div);
  }};

  document.addEventListener('click', function(e) {{
    var btn = e.target.closest && e.target.closest('.gal-remove-btn');
    if (!btn) return;
    var item = btn.closest('.gallery-item');
    if (!item) return;
    var path = item.dataset.path;
    var fieldId = item.dataset.field;
    var hidden = document.getElementById(fieldId);
    if (hidden && path) {{
      hidden.value = hidden.value.split(',').map(function(s){{return s.trim();}}).filter(function(p){{return p!==path;}}).join(',');
    }}
    item.remove();
  }});
}}
window._galReg['{field_id}'] = function(path) {{ window.galAdd('{field_id}', path); }};
</script>'''
        return mark_safe(html)


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
            # Dữ liệu cũ (vd: logo/fav) chỉ lưu tên file trần, không có tiền tố thư mục con
            rel_path = value if '/' in value else '%s/%s' % (self.subfolder, value)
            img_url = '%s%s' % (settings.MEDIA_URL, rel_path)
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
