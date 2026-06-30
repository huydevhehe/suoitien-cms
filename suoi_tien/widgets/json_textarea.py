from django import forms
from django.utils.safestring import mark_safe
import json


class JSONTextAreaWidget(forms.Textarea):
    """
    Widget hiển thị và tự động định dạng đẹp (beautify) dữ liệu JSON trong Textarea.
    Dùng inline CSS thay vì class Tailwind dark: (tránh bị purge vì class này
    chỉ tồn tại trong chuỗi Python, không nằm trong file .html để Tailwind scan).
    """
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'json-schema-textarea rounded-lg p-2 w-full',
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

    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        style = (
            '<style>'
            '.json-schema-textarea{background:#fff;color:#030712;border:1px solid #d1d5db;}'
            '.dark .json-schema-textarea{background:rgb(9 9 11);color:#e4e4e7;border-color:rgb(63 63 70);}'
            '.json-schema-textarea:focus{outline:none;box-shadow:0 0 0 1px #a855f7;border-color:#a855f7;}'
            '</style>'
        )
        return mark_safe(style + html)
