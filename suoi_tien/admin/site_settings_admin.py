"""
Quản lý Cấu hình hệ thống: Ngôn ngữ, SMTP.
"""
from django.contrib import admin
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin

from ..models import (
    LanguageProxy,
    SMTPProxy,
)
from .mixins import StatusSwitchAdminMixin


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
