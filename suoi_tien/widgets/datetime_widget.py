from django import forms
import datetime


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
