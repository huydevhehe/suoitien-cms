from unfold.widgets import UnfoldBooleanSwitchWidget


class StatusSwitchWidget(UnfoldBooleanSwitchWidget):
    """
    Switch Widget cho các trường lưu trạng thái dạng 0/1 hoặc '0'/'1' trong DB.
    Tự động chuyển đổi sang Boolean khi hiển thị và ngược lại khi lưu.
    Có hỗ trợ đảo ngược logic qua tham số 'reversed' (ví dụ: ticlock).
    """
    def __init__(self, is_char=False, reversed=False, attrs=None):
        self.is_char = is_char
        self.reversed = reversed
        super().__init__(attrs)
        # Nếu reversed=True, 0 đại diện cho Checked (Bật), 1 đại diện cho Unchecked (Tắt)
        if self.reversed:
            self.check_test = lambda v: str(v) in ('0', 'False', 'false')
        else:
            self.check_test = lambda v: str(v) in ('1', 'True', 'true')

    def value_from_datadict(self, data, files, name):
        val = super().value_from_datadict(data, files, name)
        if val:
            return '0' if self.reversed else ('1' if self.is_char else 1)
        else:
            return '1' if self.reversed else ('0' if self.is_char else 0)
