from django import forms
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
