"""
Quản lý Đơn đặt vé (TicketOrderProxy).
"""
import html

from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin

from ..models import (
    HalinkPost,
    TicketOrderProxy,
)


# ==================== FORMS ====================

class TicketOrderProxyForm(forms.ModelForm):
    STATUS_CHOICES = [
        (0, 'Chưa thanh toán'),
        (1, 'Đang xử lý'),
        (3, 'Hủy/Đơn hàng lỗi'),
        (4, 'Đã thanh toán'),
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-950 dark:text-zinc-200 rounded-lg p-2 w-full focus:ring-1 focus:ring-primary-500 focus:outline-none'
        }),
        label="Trạng thái đơn hàng"
    )

    class Meta:
        model = TicketOrderProxy
        fields = '__all__'


# ==================== MODEL ADMINS ====================

@admin.register(TicketOrderProxy)
class TicketOrderProxyAdmin(ModelAdmin):
    form = TicketOrderProxyForm
    list_per_page = 20
    # Hiển thị các cột giống giao diện PHP cũ: Mã đơn, Họ tên, SĐT, Ngày, Hình thức, Tổng tiền, Trạng thái
    list_display = ('id_cart', 'get_fullname', 'get_phone', 'date', 'get_type_payment_display', 'get_total_price_display', 'get_status_display')
    list_display_links = ('id_cart', 'get_fullname')
    search_fields = ('id_cart', 'info_user')
    list_filter = ('status', 'type_payment', 'date')
    actions = ['resend_confirmation_email']

    readonly_fields = ('render_order_details',)

    fieldsets = (
        ('Bảng thông tin tổng hợp', {
            'fields': ('render_order_details',),
        }),
        ('Trạng thái đơn hàng', {
            'fields': ('status', 'note', 'note_for_user')
        }),
    )

    def _parse_all_products(self, info_product):
        if not info_product: return "---"
        lines = info_product.split(',')
        html = ""
        total_all = 0
        try:
            for line in lines:
                parts = line.split('***+++***')
                if len(parts) >= 3:
                    pid, qty, price = parts[0], parts[1], parts[2]
                    post = HalinkPost.objects.filter(Id=pid).first()
                    title = post.title_vn if post else f"Sản phẩm #{pid}"
                    total = int(qty) * int(price)
                    total_all += total
                    html += f"<b>{title}</b><br/>Giá: {int(price):,} đ x {qty}<br/><br/>"
            html += f"<span style='color:#ef4444;font-weight:bold;font-size:16px;'>Tổng cộng: {total_all:,} đ</span>"
        except Exception as e:
            return f"<span style='color:red;'>Lỗi đọc sản phẩm: {str(e)}</span><br/>Raw: {info_product}"
        return html

    def render_order_details(self, obj):
        import html
        try:
            prod_html = self._parse_all_products(obj.info_product)

            # Khử XSS: Bọc tất cả các biến vào html.escape()
            fullname = '---'
            phone = '---'
            address = '---'
            email = '---'
            note = '---'
            if obj.info_user:
                parts = obj.info_user.split('***+++***')
                fullname = html.escape(parts[1]) if len(parts) > 1 else '---'
                phone = html.escape(parts[2]) if len(parts) > 2 else '---'
                email = html.escape(parts[3]) if len(parts) > 3 else '---'
                address = html.escape(parts[4]) if len(parts) > 4 else '---'
                note = html.escape(parts[5]) if len(parts) > 5 else '---'

            dt = ""
            if obj.date:
                try:
                    from django.utils import timezone as tz
                    local_dt = tz.localtime(obj.date)
                    dt = local_dt.strftime('%d/%m/%Y %H:%M:%S')
                except Exception:
                    dt = str(obj.date)

            payment_map = {0: 'Chưa chọn', 1: 'Tiền mặt', 2: 'Chuyển khoản', 3: 'ShopeePay', 4: 'Momo', 5: 'ZaloPay'}
            payment_str = payment_map.get(obj.type_payment, f"Khác ({obj.type_payment})")

            status_map = {0: 'Chưa thanh toán', 1: 'Đang xử lý', 3: 'Hủy/Lỗi', 4: 'Đã thanh toán'}
            status_str = status_map.get(obj.status, f"Trạng thái {obj.status}")

            if obj.status == 4:
                status_html = f'<span style="color:#10b981; font-weight:bold;">✔ {status_str}</span>'
            elif obj.status == 3:
                status_html = f'<span style="color:#ef4444; font-weight:bold;">✘ {status_str}</span>'
            else:
                status_html = f'<span style="color:#fbbf24; font-weight:bold;">● {status_str}</span>'

            html_content = f"""
            <div style="display: flex; gap: 20px; font-family: sans-serif; color:#ddd; font-size:14px; line-height:1.6;">
                <div style="flex: 1; background: #1a1a1a; padding: 20px; border-radius: 8px; border:1px solid #333;">
                    <h3 style="margin-top:0; border-bottom:1px solid #333; padding-bottom:10px; color:#fff;">Thông tin thanh toán</h3>
                    <p style="margin:5px 0;"><b>Mã đơn hàng:</b> {obj.id_cart}</p>
                    <p style="margin:5px 0;"><b>Thời gian:</b> {dt}</p>
                    <p style="margin:5px 0;"><b>Phương thức thanh toán:</b> {payment_str}</p>
                    <p style="margin:5px 0;"><b>Trạng thái:</b> {status_html}</p>
                    <br/>
                    <h3 style="margin-top:0; border-bottom:1px solid #333; padding-bottom:10px; color:#fff;">Dịch vụ đã đặt</h3>
                    <div>{prod_html}</div>
                </div>

                <div style="flex: 1; background: #1a1a1a; padding: 20px; border-radius: 8px; border:1px solid #333;">
                    <h3 style="margin-top:0; border-bottom:1px solid #333; padding-bottom:10px; color:#fff;">Thông tin khách hàng</h3>
                    <p style="margin:5px 0;"><b>Họ tên:</b> {fullname}</p>
                    <p style="margin:5px 0;"><b>Email:</b> {email}</p>
                    <p style="margin:5px 0;"><b>Địa chỉ:</b> {address}</p>
                    <p style="margin:5px 0;"><b>SĐT:</b> {phone}</p>
                    <p style="margin:5px 0;"><b>Ghi chú:</b> {note}</p>
                </div>
            </div>
            """
            return mark_safe(html_content)
        except Exception as e:
            return f"Xảy ra lỗi khi hiển thị giao diện: {str(e)}"
    render_order_details.short_description = ' '

    def get_fullname(self, obj):
        if obj.info_user:
            parts = obj.info_user.split('***+++***')
            return parts[1] if len(parts) > 1 else 'N/A'
        return 'N/A'
    get_fullname.short_description = 'Họ tên'

    def get_phone(self, obj):
        if obj.info_user:
            parts = obj.info_user.split('***+++***')
            return parts[2] if len(parts) > 2 else 'N/A'
        return 'N/A'
    get_phone.short_description = 'SĐT'

    def get_total_price_display(self, obj):
        return f"{obj.computed_total_price_formatted} đ"
    get_total_price_display.short_description = 'Tổng tiền'

    def get_status_display(self, obj):
        if obj.status == 4:
            return 'Đã thanh toán'
        elif obj.status == 1:
            return 'Đang xử lý'
        elif obj.status == 3:
            return 'Hủy/Đơn hàng lỗi'
        return 'Chưa thanh toán'
    get_status_display.short_description = 'Tình trạng'

    def get_type_payment_display(self, obj):
        payment_map = {
            0: 'Chưa chọn',
            1: 'Tiền mặt',
            2: 'Chuyển khoản',
            3: 'ShopeePay',
            4: 'Momo',
            5: 'ZaloPay'
        }
        val = payment_map.get(obj.type_payment, f"Khác ({obj.type_payment})")
        colors = {
            0: '#9ca3af',  # gray
            1: '#10b981',  # green
            2: '#3b82f6',  # blue
            3: '#f97316',  # orange
            4: '#ec4899',  # pink
            5: '#06b6d4'   # cyan
        }
        color = colors.get(obj.type_payment, '#6b7280')
        return format_html('<span style="color: {}; font-weight: 500;">{}</span>', color, val)
    get_type_payment_display.short_description = 'Hình thức thanh toán'

    def resend_confirmation_email(self, request, queryset):
        sent_count = 0
        error_count = 0
        for order in queryset:
            try:
                if order.info_user:
                    parts = order.info_user.split('***+++***')
                    email = parts[3] if len(parts) > 3 else None
                    fullname = html.escape(parts[1]) if len(parts) > 1 else 'Quý khách'

                    if email and '@' in email:
                        from ..utils import send_email_via_smtp_proxy
                        subject = f"Xác nhận đơn đặt vé #{order.id_cart} - Công viên văn hóa Suối Tiên"
                        prod_html = self._parse_all_products(order.info_product)
                        body_html = f"""
                        <html>
                        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                            <h2 style="color: #0284c7;">Kính gửi {fullname},</h2>
                            <p>Chúng tôi xin gửi lại thông tin xác nhận đơn đặt vé của quý khách tại Suối Tiên Theme Park:</p>
                            <div style="background: #f3f4f6; padding: 15px; border-radius: 6px; margin: 15px 0;">
                                <p style="margin: 5px 0;"><b>Mã đơn hàng:</b> {order.id_cart}</p>
                                <p style="margin: 5px 0;"><b>Thời gian đặt:</b> {order.date.strftime('%d/%m/%Y %H:%M:%S') if order.date else '---'}</p>
                                <p style="margin: 5px 0;"><b>Tổng thanh toán:</b> {order.computed_total_price_formatted} đ</p>
                            </div>
                            <h3 style="border-bottom: 2px solid #0284c7; padding-bottom: 5px;">Chi tiết đặt vé</h3>
                            <div style="margin-bottom: 20px;">{prod_html}</div>
                            <hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 20px 0;"/>
                            <p style="font-size: 12px; color: #6b7280;">Đây là thư tự động từ hệ thống quản lý Suối Tiên Theme Park. Vui lòng không trả lời thư này.</p>
                        </body>
                        </html>
                        """
                        send_email_via_smtp_proxy(email.strip(), subject, body_html)
                        sent_count += 1
                    else:
                        error_count += 1
                else:
                    error_count += 1
            except Exception:
                error_count += 1

        self.message_user(
            request,
            f"Đã gửi lại email xác nhận cho {sent_count} đơn đặt vé." +
            (f" Thất bại: {error_count} đơn hàng do không có email hợp lệ hoặc lỗi kết nối." if error_count > 0 else "")
        )
    resend_confirmation_email.short_description = "Gửi lại email xác nhận đơn hàng"
