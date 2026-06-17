"""
Quản lý Nội dung: Bài viết, Chuyên mục bài viết, Trang tĩnh,
Sản phẩm, Chuyên mục sản phẩm, Banner/Quảng cáo, Menu, Cấu hình Website.
"""
import os
import time

from django.contrib import admin
from django import forms
from django.conf import settings
from django.db.models import Subquery, OuterRef
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from ..models import (
    HalinkPost,
    HalinkFlash,
    HalinkMenu,
    HalinkMeta,
    HalinkMetabox,
    HalinkStatistic,
    HalinkWebsite,
    PostProxy,
    PostCategoryProxy,
    PageProxy,
    ProductProxy,
    ProductCategoryProxy,
)
from .mixins import (
    PostDisplayMixin,
    TinyMCEAdminMixin,
    MultiLangAdminMixin,
    CategoryAdminMixin,
    ImagePickerAdminMixin,
    SidebarAdminMixin,
    StatusSwitchAdminMixin,
    UnixTimestampDateTimeAdminMixin,
    JSONSchemaAdminMixin,
    SortableAdminMixin,
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

class ProductAdminForm(forms.ModelForm):
    price = forms.IntegerField(
        label="Giá bán", 
        required=False, 
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'border bg-white font-medium rounded-md shadow-sm text-gray-900 w-full focus:ring focus:ring-primary-300 focus:border-primary-600 px-3 py-2 sm:text-sm dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700'
        })
    )
    promo_price = forms.IntegerField(
        label="Giá khuyến mãi", 
        required=False, 
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'border bg-white font-medium rounded-md shadow-sm text-gray-900 w-full focus:ring focus:ring-primary-300 focus:border-primary-600 px-3 py-2 sm:text-sm dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700'
        })
    )

    class Meta:
        model = ProductProxy
        fields = [
            'title_vn', 'alias', 'description_vn', 'content_vn', 
            'price', 'promo_price', 'post_image', 'post_gallery', 
            'idcat', 'sort', 'ticlock', 'home'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Truy vấn giá bán hiện tại
            price_meta = HalinkMeta.objects.filter(Id_post=self.instance.pk, meta_title='halink_metabox_gia').first()
            if price_meta and price_meta.meta_value:
                try:
                    self.fields['price'].initial = int(price_meta.meta_value)
                except (ValueError, TypeError):
                    self.fields['price'].initial = price_meta.meta_value
            
            # Truy vấn giá khuyến mãi hiện tại
            promo_meta = HalinkMeta.objects.filter(Id_post=self.instance.pk, meta_title='halink_metabox_gia_khuyen_mai').first()
            if promo_meta and promo_meta.meta_value:
                try:
                    self.fields['promo_price'].initial = int(promo_meta.meta_value)
                except (ValueError, TypeError):
                    self.fields['promo_price'].initial = promo_meta.meta_value


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
            local_path = os.path.join(settings.MEDIA_ROOT, obj.file_vn)
            if os.path.exists(local_path):
                url = f"{settings.MEDIA_URL}{obj.file_vn}"
            else:
                # File không tồn tại ở local → hiển thị placeholder SVG (không gọi mạng)
                url = (
                    "data:image/svg+xml;utf8,"
                    "<svg xmlns='http://www.w3.org/2000/svg' width='30' height='30' viewBox='0 0 30 30'>"
                    "<rect width='30' height='30' rx='4' fill='%23e5e7eb'/>"
                    "<text x='50%25' y='54%25' text-anchor='middle' dominant-baseline='middle' "
                    "font-size='12' fill='%239ca3af'>?</text></svg>"
                )
            return format_html('<img src="{}" width="30" height="30" style="object-fit:cover; border-radius:4px; margin-right:10px; vertical-align:middle;"/> {}', url, name)
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


# ==============================================================================
# PROXY MODELS ADMINS - NỘI DUNG (Bài viết, Sản phẩm, Trang)
# ==============================================================================

@admin.register(PostProxy)
class PostProxyAdmin(JSONSchemaAdminMixin, SortableAdminMixin, StatusSwitchAdminMixin, CategoryAdminMixin, ImagePickerAdminMixin, SidebarAdminMixin, UnixTimestampDateTimeAdminMixin, PostDisplayMixin, TinyMCEAdminMixin, MultiLangAdminMixin, ModelAdmin):
    category_type = 'postcat'  # Chuyên mục bài viết
    list_per_page = 20
    list_display = ('get_image', 'get_clean_title', 'get_category_display', 'display_sort_actions', 'get_hot_display', 'get_status_display', 'get_author_display', 'get_date_display')
    list_display_links = ('get_image', 'get_clean_title')
    search_fields = ('title_vn', 'content_vn', 'alias')
    list_filter = ('ticlock', 'date')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(post_type='post')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.post_type = 'post'
            if not obj.date:  # PHP: date = time() khi tao moi
                obj.date = int(time.time())
        super().save_model(request, obj, form, change)


@admin.register(PostCategoryProxy)
class PostCategoryProxyAdmin(JSONSchemaAdminMixin, SortableAdminMixin, StatusSwitchAdminMixin, CategoryAdminMixin, ImagePickerAdminMixin, SidebarAdminMixin, UnixTimestampDateTimeAdminMixin, PostDisplayMixin, TinyMCEAdminMixin, MultiLangAdminMixin, ModelAdmin):
    category_type = 'postcat'
    list_per_page = 20
    
    def display_hierarchical_title(self, obj):
        if obj.idcat:
            return format_html('<span style="color: #a78bfa; font-weight: bold;">|— </span>{}', obj.clean_title)
        return obj.clean_title
    display_hierarchical_title.short_description = "Tiêu đề"

    # Cột giống PHP: Ảnh, Tiêu đề, Nổi bật, Trạng thái, Tác giả, Thời gian
    list_display = ('get_image', 'display_hierarchical_title', 'display_sort_actions', 'get_hot_display', 'get_status_display', 'get_author_display', 'get_date_display')
    list_display_links = ('get_image', 'get_clean_title')
    search_fields = ('title_vn', 'alias')
    list_filter = ('ticlock',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(post_type='postcat')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.post_type = 'postcat'
            if not obj.date:
                obj.date = int(time.time())
        super().save_model(request, obj, form, change)


@admin.register(PageProxy)
class PageProxyAdmin(StatusSwitchAdminMixin, UnixTimestampDateTimeAdminMixin, PostDisplayMixin, TinyMCEAdminMixin, MultiLangAdminMixin, ModelAdmin):
    list_display = ('Id', 'get_clean_title', 'alias', 'get_status_display', 'get_date_display')
    list_display_links = ('Id', 'get_clean_title')
    search_fields = ('title_vn', 'content_vn', 'alias')
    list_filter = ('ticlock',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(post_type='page')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.post_type = 'page'
            if not obj.date:
                obj.date = int(time.time())
        super().save_model(request, obj, form, change)


@admin.register(ProductProxy)
class ProductProxyAdmin(JSONSchemaAdminMixin, SortableAdminMixin, StatusSwitchAdminMixin, CategoryAdminMixin, ImagePickerAdminMixin, SidebarAdminMixin, UnixTimestampDateTimeAdminMixin, PostDisplayMixin, TinyMCEAdminMixin, MultiLangAdminMixin, ModelAdmin):
    category_type = 'productcat'  # Danh mục sản phẩm
    form = ProductAdminForm
    list_display = ('get_image', 'get_clean_title', 'get_price', 'get_category_display', 'display_sort_actions', 'get_status_display', 'get_date_display')
    list_display_links = ('get_image', 'get_clean_title')
    search_fields = ('title_vn', 'description_vn', 'content_vn')
    list_filter = ('ticlock', 'date')

    def get_queryset(self, request):
        price_subquery = HalinkMeta.objects.filter(
            Id_post=OuterRef('Id'),
            meta_title='halink_metabox_gia'
        ).values('meta_value')[:1]

        promo_subquery = HalinkMeta.objects.filter(
            Id_post=OuterRef('Id'),
            meta_title='halink_metabox_gia_khuyen_mai'
        ).values('meta_value')[:1]
        
        return super().get_queryset(request).filter(post_type='product').annotate(
            price_val=Subquery(price_subquery),
            promo_val=Subquery(promo_subquery)
        )

    def get_price(self, obj):
        p_str = getattr(obj, 'price_val', None)
        pr_str = getattr(obj, 'promo_val', None)
        
        p_val = 0
        pr_val = 0
        if p_str:
            try:
                p_val = int(p_str.strip())
            except ValueError:
                pass
        if pr_str:
            try:
                pr_val = int(pr_str.strip())
            except ValueError:
                pass

        if pr_val > 0:
            return format_html(
                '<span style="text-decoration: line-through; color: #888; margin-right: 8px;">{} đ</span>'
                '<span style="color: #ef4444; font-weight: bold;">{} đ</span>',
                f"{p_val:,}", f"{pr_val:,}"
            )
        elif p_val > 0:
            return format_html('<span style="font-weight: 500;">{} đ</span>', f"{p_val:,}")
        
        if p_str:
            return p_str
        return "Liên hệ"
    get_price.short_description = "Giá bán"
    get_price.admin_order_field = 'price_val'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.post_type = 'product'
            if not obj.date:
                obj.date = int(time.time())
        super().save_model(request, obj, form, change)

        # Lưu metadata giá bán từ form
        from django.utils import timezone
        price_val = form.cleaned_data.get('price')
        if price_val is not None:
            meta, created = HalinkMeta.objects.get_or_create(
                Id_post=obj.pk,
                meta_title='halink_metabox_gia',
                defaults={'meta_type': 'product', 'ticlock': 0, 'date': timezone.now()}
            )
            meta.meta_value = str(price_val)
            meta.save()

        promo_val = form.cleaned_data.get('promo_price')
        if promo_val is not None:
            meta, created = HalinkMeta.objects.get_or_create(
                Id_post=obj.pk,
                meta_title='halink_metabox_gia_khuyen_mai',
                defaults={'meta_type': 'product', 'ticlock': 0, 'date': timezone.now()}
            )
            meta.meta_value = str(promo_val)
            meta.save()


@admin.register(ProductCategoryProxy)
class ProductCategoryProxyAdmin(JSONSchemaAdminMixin, SortableAdminMixin, StatusSwitchAdminMixin, CategoryAdminMixin, ImagePickerAdminMixin, SidebarAdminMixin, UnixTimestampDateTimeAdminMixin, PostDisplayMixin, TinyMCEAdminMixin, MultiLangAdminMixin, ModelAdmin):
    category_type = 'productcat'
    
    def display_hierarchical_title(self, obj):
        if obj.idcat:
            return format_html('<span style="color: #a78bfa; font-weight: bold;">|— </span>{}', obj.clean_title)
        return obj.clean_title
    display_hierarchical_title.short_description = "Tiêu đề"
    
    list_display = ('Id', 'display_hierarchical_title', 'alias', 'display_sort_actions', 'get_status_display', 'get_date_display')
    list_display_links = ('Id', 'get_clean_title')
    search_fields = ('title_vn', 'alias')
    list_filter = ('ticlock',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(post_type='productcat')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.post_type = 'productcat'
            if not obj.date:
                obj.date = int(time.time())
        super().save_model(request, obj, form, change)
