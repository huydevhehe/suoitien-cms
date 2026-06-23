from django import forms
import re


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
