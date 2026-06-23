"""
Quản lý Cấu hình hiển thị: Banner/Quảng cáo, Menu, Cấu hình Website, Thống kê, Metabox/Meta.
"""
import os

from django.contrib import admin
from django import forms
from django.conf import settings
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from ..models import (
    HalinkFlash,
    HalinkMenu,
    HalinkMeta,
    HalinkMetabox,
    HalinkStatistic,
    HalinkWebsite,
)
from .mixins import (
    PostDisplayMixin,
    TinyMCEAdminMixin,
    MultiLangAdminMixin,
    ImagePickerAdminMixin,
    StatusSwitchAdminMixin,
    UnixTimestampDateTimeAdminMixin,
    JSONSchemaAdminMixin,
)
from .widgets import MenuBuilderWidget

# ==================== FORMS ====================

class HalinkMenuForm(forms.ModelForm):
    class Meta:
        model = HalinkMenu
        fields = '__all__'
        widgets = {
            'content_menu': MenuBuilderWidget()
        }


# ==================== MODEL ADMINS ====================

# 4. Quản lý Banner & Quảng cáo / Thư viện
@admin.register(HalinkFlash)
class HalinkFlashAdmin(StatusSwitchAdminMixin, UnixTimestampDateTimeAdminMixin, ImagePickerAdminMixin, PostDisplayMixin, MultiLangAdminMixin, ModelAdmin):
    list_per_page = 20
    list_display = ('get_filename', 'get_dimensions', 'get_size', 'get_status_display', 'get_date_display')
    search_fields = ('title_vn', 'file_vn', 'link')
    list_filter = ('ticlock',)

    def get_filename(self, obj):
        if obj.file_vn:
            name = obj.file_vn.split('/')[-1] if '/' in obj.file_vn else obj.file_vn

            # Thử đường dẫn gốc
            local_path = os.path.join(settings.MEDIA_ROOT, obj.file_vn.lstrip('/'))
            url = f"{settings.MEDIA_URL}{obj.file_vn.lstrip('/')}"

            # Nếu không thấy, thử tìm file rác nằm trực tiếp trong thư mục media/ (do migrate từ PHP)
            if not os.path.exists(local_path):
                fallback_path = os.path.join(settings.MEDIA_ROOT, name)
                if os.path.exists(fallback_path):
                    local_path = fallback_path
                    url = f"{settings.MEDIA_URL}{name}"

            if os.path.exists(local_path):
                return format_html('<img src="{}" width="30" height="30" style="object-fit:cover; border-radius:4px; margin-right:10px; vertical-align:middle;"/> {}', url, name)
            else:
                # File không tồn tại ở local → hiển thị placeholder SVG (không gọi mạng)
                placeholder = (
                    "data:image/svg+xml;utf8,"
                    "<svg xmlns='http://www.w3.org/2000/svg' width='30' height='30' viewBox='0 0 30 30'>"
                    "<rect width='30' height='30' rx='4' fill='%23e5e7eb'/>"
                    "<text x='50%25' y='54%25' text-anchor='middle' dominant-baseline='middle' "
                    "font-size='12' fill='%239ca3af'>?</text></svg>"
                )
                return format_html('<img src="{}" width="30" height="30" style="object-fit:cover; border-radius:4px; margin-right:10px; vertical-align:middle;"/> {}', placeholder, name)
        return obj.title_vn
    get_filename.short_description = 'Tên tập tin'

    def get_dimensions(self, obj):
        if obj.width and obj.height:
            return f"{obj.width}x{obj.height} px"
        return "---"
    get_dimensions.short_description = 'Kích thước'

    def get_size(self, obj):
        # Database gốc không lưu dung lượng. PHP cũ đọc trực tiếp dung lượng từ file trong thư mục upload/.
        # Đoạn code dưới đây giả lập tính năng đó của PHP: nếu có file thực tế trên server, nó sẽ tính ra dung lượng.
        if obj.file_vn:
            file_path = os.path.join(settings.MEDIA_ROOT, obj.file_vn.replace('/', '\\'))
            if os.path.exists(file_path):
                try:
                    size_bytes = os.path.getsize(file_path)
                    if size_bytes >= 1048576:
                        return f"{size_bytes / 1048576:.0f} MB"
                    return f"{size_bytes / 1024:.0f} KB"
                except:
                    pass
        return "---"
    get_size.short_description = 'Dung lượng'

# 5. Quản lý Menu
@admin.register(HalinkMenu)
class HalinkMenuAdmin(StatusSwitchAdminMixin, PostDisplayMixin, MultiLangAdminMixin, ModelAdmin):
    form = HalinkMenuForm
    list_per_page = 20
    list_display = ('Id', 'get_clean_title', 'id_cat', 'get_status_display')
    search_fields = ('title_cat',)
    list_filter = ('ticlock',)

# 6. Cấu hình Website
@admin.register(HalinkWebsite)
class HalinkWebsiteAdmin(JSONSchemaAdminMixin, StatusSwitchAdminMixin, PostDisplayMixin, TinyMCEAdminMixin, MultiLangAdminMixin, ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'get_clean_title', 'hotline', 'email', 'get_clean_diachi')
    search_fields = ('title', 'email', 'hotline')

    fieldsets = (
        ('Nhận dạng site', {
            'classes': ('tab',),
            'fields': ('tencty', 'slogan', 'logo', 'fav', 'opentime', 'closetime'),
        }),
        ('Cấu hình Địa chỉ/Mạng xã hội', {
            'classes': ('tab',),
            'fields': ('hotline', 'hotline2', 'email', 'diachi', 'fanpage', 'youtube', 'twitter', 'google', 'instagram', 'linkedin'),
        }),
        ('Cấu hình SEO', {
            'classes': ('tab',),
            'fields': ('title', 'keyword', 'description', 'googleanalytics', 'googlemap', 'schema_home'),
        }),
        ('Cấu hình hệ thống', {
            'classes': ('tab',),
            'fields': ('enable', 'thugon_menu', 'theme', 'st_accesstoken', 'st_accesstoken_ex'),
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# 7. Thống kê truy cập
@admin.register(HalinkStatistic)
class HalinkStatisticAdmin(ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'ip', 'id_post', 'url', 'browser', 'date')
    search_fields = ('ip', 'url')
    list_filter = ('date', 'browser')

# 8. Cấu hình Metabox và Meta
@admin.register(HalinkMetabox)
class HalinkMetaboxAdmin(ModelAdmin):
    list_per_page = 20
    list_display = ('Id', 'meta_title', 'meta_key', 'meta_type', 'post_type', 'ticlock')
    search_fields = ('meta_title', 'meta_key')

@admin.register(HalinkMeta)
class HalinkMetaAdmin(ModelAdmin):
    list_per_page = 20
    list_display = ('Id', 'Id_post', 'meta_title', 'meta_type', 'date', 'ticlock')
    search_fields = ('meta_title', 'meta_value')
    list_filter = ('meta_type', 'ticlock')
