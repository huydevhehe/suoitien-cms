from django import forms
from django.utils.safestring import mark_safe


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
