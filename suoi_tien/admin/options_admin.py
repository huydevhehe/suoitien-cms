"""
Quản lý Tùy chọn: Bình luận, Hỗ trợ, Ngôn ngữ, Cấu hình SMTP.
"""
from django.contrib import admin
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin

from ..models import (
    CommentProxy,
    SupportProxy,
    LanguageProxy,
    SMTPProxy,
)
from .mixins import StatusSwitchAdminMixin


@admin.register(CommentProxy)
class CommentProxyAdmin(StatusSwitchAdminMixin, ModelAdmin):
    list_per_page = 20
    list_display = ('Id', 'get_id_post', 'get_fullname', 'get_phone', 'get_content', 'get_star', 'date', 'get_status')
    search_fields = ('meta_value',)
    list_filter = ('ticlock', 'date')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(meta_type='comment_post')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.meta_type = 'comment_post'
        super().save_model(request, obj, form, change)

    def get_id_post(self, obj):
        return obj.Id_post or '---'
    get_id_post.short_description = 'Mã liên kết'

    def get_fullname(self, obj):
        return obj.fullname or '---'
    get_fullname.short_description = 'Họ tên'

    def get_phone(self, obj):
        return obj.phone or '---'
    get_phone.short_description = 'Số điện thoại'

    def get_content(self, obj):
        return obj.content or '---'
    get_content.short_description = 'Nội dung bình luận'

    def get_star(self, obj):
        return f"{obj.star} ★" if obj.star else '---'
    get_star.short_description = 'Đánh giá'

    def get_status(self, obj):
        if obj.ticlock == 0:
            return mark_safe('<span style="color:#10b981; font-weight:bold;">✔ Đã duyệt</span>')
        return mark_safe('<span style="color:#ef4444; font-weight:bold;">✘ Chưa duyệt</span>')
    get_status.short_description = 'Trạng thái'


@admin.register(SupportProxy)
class SupportProxyAdmin(StatusSwitchAdminMixin, ModelAdmin):
    list_per_page = 20
    list_display = ('Id', 'get_id_post', 'get_subject', 'get_message', 'date', 'get_status')
    search_fields = ('meta_title', 'meta_value')
    list_filter = ('ticlock', 'date')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(meta_type='support')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.meta_type = 'support'
        super().save_model(request, obj, form, change)

    def get_id_post(self, obj):
        return obj.Id_post or '---'
    get_id_post.short_description = 'Mã liên kết'

    def get_subject(self, obj):
        return obj.meta_title or '---'
    get_subject.short_description = 'Chủ đề hỗ trợ'

    def get_message(self, obj):
        return obj.meta_value or '---'
    get_message.short_description = 'Nội dung hỗ trợ'

    def get_status(self, obj):
        if obj.ticlock == 0:
            return mark_safe('<span style="color:#10b981; font-weight:bold;">✔ Đã xử lý</span>')
        return mark_safe('<span style="color:#fbbf24; font-weight:bold;">● Chờ xử lý</span>')
    get_status.short_description = 'Trạng thái'


@admin.register(LanguageProxy)
class LanguageProxyAdmin(StatusSwitchAdminMixin, ModelAdmin):
    list_per_page = 20
    list_display = ('Id', 'get_key', 'get_val', 'get_status')
    search_fields = ('meta_title', 'meta_value')
    list_filter = ('ticlock',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(meta_type='halinklanguage')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.meta_type = 'halinklanguage'
        super().save_model(request, obj, form, change)

    def get_key(self, obj):
        return obj.meta_title or '---'
    get_key.short_description = 'Mã từ khóa'

    def get_val(self, obj):
        return obj.meta_value or '---'
    get_val.short_description = 'Giá trị hiển thị'

    def get_status(self, obj):
        if obj.ticlock == 0:
            return mark_safe('<span style="color:#10b981; font-weight:bold;">✔ Kích hoạt</span>')
        return mark_safe('<span style="color:#ef4444; font-weight:bold;">✘ Tắt</span>')
    get_status.short_description = 'Trạng thái'


@admin.register(SMTPProxy)
class SMTPProxyAdmin(StatusSwitchAdminMixin, ModelAdmin):
    list_per_page = 20
    list_display = ('Id', 'get_key', 'get_val', 'get_status')
    search_fields = ('meta_title', 'meta_value')
    list_filter = ('ticlock',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(meta_type='halinksmtp')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.meta_type = 'halinksmtp'
        super().save_model(request, obj, form, change)

    def get_key(self, obj):
        return obj.meta_title or '---'
    get_key.short_description = 'Cấu hình SMTP'

    def get_val(self, obj):
        return obj.meta_value or '---'
    get_val.short_description = 'Giá trị cấu hình'

    def get_status(self, obj):
        if obj.ticlock == 0:
            return mark_safe('<span style="color:#10b981; font-weight:bold;">✔ Hoạt động</span>')
        return mark_safe('<span style="color:#ef4444; font-weight:bold;">✘ Tắt</span>')
    get_status.short_description = 'Trạng thái'
