from django.contrib import admin
import datetime
import os
from django.conf import settings
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin
import html
from django.db.models import Subquery, OuterRef

# Allow active staff and superusers to access Django Admin

from .models import (
    HalinkAdmin,
    HalinkUser,
    HalinkPost,
    HalinkCart,
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
    TicketOrderProxy,
    FoodOrderProxy,
    SupportProxy,
    CommentProxy,
    LanguageProxy,
    SMTPProxy,
)

class PostDisplayMixin:
    def get_clean_title(self, obj):
        return obj.clean_title
    get_clean_title.short_description = "Tiêu đề"

    def get_clean_diachi(self, obj):
        return obj.clean_diachi
    get_clean_diachi.short_description = "Địa chỉ"

    def get_image(self, obj):
        if obj.post_image:
            local_path = os.path.join(settings.MEDIA_ROOT, obj.post_image)
            if os.path.exists(local_path):
                url = f"{settings.MEDIA_URL}{obj.post_image}"
            else:
                url = f"https://suoitien.vn/upload/hinhanh/{obj.post_image}"
            return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:50%;" />', url)
        return ''
    get_image.short_description = 'Ảnh'

    def get_category_display(self, obj):
        if obj.idcat:
            try:
                cat_id = obj.idcat.strip(',').split(',')[0]
                from .models import PostCategoryProxy, ProductCategoryProxy
                cat = PostCategoryProxy.objects.filter(Id=cat_id).first() or ProductCategoryProxy.objects.filter(Id=cat_id).first()
                return cat.clean_title if cat else '---'
            except Exception:
                pass
        return '---'
    get_category_display.short_description = 'Danh mục'

    def get_hot_display(self, obj):
        if obj.home == 1:
            return mark_safe('<span style="color:#fbbf24; font-size:16px;">★</span>')
        return ''
    get_hot_display.short_description = 'Nổi bật'

    def get_status_display(self, obj):
        if str(obj.ticlock) == '0':
            return mark_safe('<span style="color:#10b981; font-weight:bold;">✔</span>')
        return mark_safe('<span style="color:#ef4444; font-weight:bold;">✘</span>')
    get_status_display.short_description = 'Trạng thái'

    def get_author_display(self, obj):
        return 'admin'
    get_author_display.short_description = 'Tác giả'

    def get_date_display(self, obj):
        if obj.date:
            try:
                return datetime.datetime.fromtimestamp(int(obj.date)).strftime('%d/%m/%Y %H:%M')
            except:
                return obj.date
        return '---'
    get_date_display.short_description = 'Thời gian'


class TinyMCEAdminMixin:
    class Media:
        js = (
            'https://cdn.jsdelivr.net/npm/tinymce@6/tinymce.min.js',
            'admin/js/tinymce_init.js',
        )


class MultiLangAdminMixin:
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in [
            'title_vn', 'title_cat', 'description_vn', 'content_vn',
            'title', 'diachi', 'tencty', 'slogan', 'message', 'description'
        ]:
            from django.db import models
            from .widgets import MultiLangWidget
            widget_class = forms.Textarea if (isinstance(db_field, models.TextField) or db_field.name in ['message']) else forms.TextInput
            kwargs['widget'] = MultiLangWidget(widget_class=widget_class)
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class CategoryAdminMixin:
    """Mixin gắn CategoryCheckboxWidget vào field idcat."""
    category_type = 'postcat'  # Override trong từng admin class

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'idcat':
            from .widgets import CategoryCheckboxWidget
            kwargs['widget'] = CategoryCheckboxWidget(category_type=self.category_type)
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class ImagePickerAdminMixin:
    """Mixin gắn ImagePickerWidget vào các field hình ảnh."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ['post_image', 'post_banner']:
            from .widgets import ImagePickerWidget
            kwargs['widget'] = ImagePickerWidget(subfolder='hinhanh')
            return db_field.formfield(**kwargs)
        elif db_field.name == 'file_vn':
            from .widgets import ImagePickerWidget
            kwargs['widget'] = ImagePickerWidget(subfolder='flash')
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class SidebarAdminMixin:
    """Mixin gắn SidebarCheckboxWidget vào field post_sidebar."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'post_sidebar':
            from .widgets import SidebarCheckboxWidget
            kwargs['widget'] = SidebarCheckboxWidget()
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class StatusSwitchAdminMixin:
    """Mixin tự động áp dụng StatusSwitchWidget cho các trường trạng thái dạng 0/1 hoặc '0'/'1'."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ['ticlock', 'home', 'fullwidth', 'enable', 'thugon_menu']:
            from django.db import models
            from .widgets import StatusSwitchWidget
            is_char = isinstance(db_field, (models.CharField, models.TextField))
            kwargs['widget'] = StatusSwitchWidget(is_char=is_char)
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class UnixTimestampDateTimeAdminMixin:
    """Mixin gắn UnixTimestampDateTimeWidget vào các trường lưu Unix Timestamp dạng số."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'date' and db_field.model.__name__ in ['HalinkFlash', 'HalinkFlashAdmin']:
            from .widgets import UnixTimestampDateTimeWidget
            kwargs['widget'] = UnixTimestampDateTimeWidget()
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class JSONSchemaAdminMixin:
    """Mixin tự động áp dụng JSONTextAreaWidget cho các trường Schema JSON-LD."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ['schema_org', 'schema_home']:
            from .widgets import JSONTextAreaWidget
            kwargs['widget'] = JSONTextAreaWidget()
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class SortableAdminMixin:
    """Mixin cung cấp nút dịch chuyển Lên/Xuống cho trường 'sort' trong Django Admin list view."""

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/move-up/', self.admin_site.admin_view(self.move_up), name='move_up'),
            path('<path:object_id>/move-down/', self.admin_site.admin_view(self.move_down), name='move_down'),
        ]
        return custom_urls + urls

    def move_up(self, request, object_id):
        if request.method != 'POST':
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Must use POST request")
        obj = self.get_object(request, object_id)
        if not self.has_change_permission(request, obj):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to edit this object.")
        if obj and hasattr(obj, 'sort'):
            # Lấy đối tượng liền trước (có sort nhỏ hơn)
            prev_obj = self.model.objects.filter(sort__lt=obj.sort).order_by('-sort').first()
            if prev_obj:
                obj.sort, prev_obj.sort = prev_obj.sort, obj.sort
                obj.save()
                prev_obj.save()
            else:
                obj.sort = (obj.sort or 0) - 1
                obj.save()
        from django.shortcuts import redirect
        return redirect(request.META.get('HTTP_REFERER', '../'))

    def move_down(self, request, object_id):
        if request.method != 'POST':
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Must use POST request")
        obj = self.get_object(request, object_id)
        if not self.has_change_permission(request, obj):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to edit this object.")
        if obj and hasattr(obj, 'sort'):
            # Lấy đối tượng liền sau (có sort lớn hơn)
            next_obj = self.model.objects.filter(sort__gt=obj.sort).order_by('sort').first()
            if next_obj:
                obj.sort, next_obj.sort = next_obj.sort, obj.sort
                obj.save()
                next_obj.save()
            else:
                obj.sort = (obj.sort or 0) + 1
                obj.save()
        from django.shortcuts import redirect
        return redirect(request.META.get('HTTP_REFERER', '../'))

    def display_sort_actions(self, obj):
        if not hasattr(obj, 'sort') or obj.sort is None:
            return '---'
        js_onclick = "event.preventDefault(); var f=document.createElement('form'); f.method='post'; f.action=this.href; var c=document.querySelector('input[name=csrfmiddlewaretoken]'); if(c) f.appendChild(c.cloneNode(true)); document.body.appendChild(f); f.submit();"
        return format_html(
            '<div style="display:flex; gap:4px; align-items:center;">'
            '<a href="{}/move-up/" onclick="{}" style="display:inline-flex; align-items:center; justify-content:center; width:22px; height:22px; background:#e0f2fe; color:#0369a1; border-radius:4px; font-weight:bold; text-decoration:none;" title="Di chuyển lên">▲</a>'
            '<span style="min-width:20px; text-align:center; font-weight:600;">{}</span>'
            '<a href="{}/move-down/" onclick="{}" style="display:inline-flex; align-items:center; justify-content:center; width:22px; height:22px; background:#fee2e2; color:#b91c1c; border-radius:4px; font-weight:bold; text-decoration:none;" title="Di chuyển xuống">▼</a>'
            '</div>',
            obj.pk, js_onclick, obj.sort, obj.pk, js_onclick
        )
    display_sort_actions.short_description = "Thứ tự"
    display_sort_actions.admin_order_field = 'sort'









# ==================== FORMS ====================

class HalinkAdminPasswordForm(forms.ModelForm):
    """Form quản lý mật khẩu Admin CMS - hiển thị field password riêng."""
    new_password = forms.CharField(
        label='Mật khẩu mới',
        widget=forms.PasswordInput(attrs={'placeholder': 'Để trống nếu không đổi'}),
        required=False,
        help_text='Nhập mật khẩu mới. Để trống nếu không thay đổi. Sẽ tự động hash md5(md5()) giống PHP cũ.'
    )

    class Meta:
        model = HalinkAdmin
        exclude = ['password']

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_pw = self.cleaned_data.get('new_password')
        if new_pw:
            instance.password = new_pw  # save() trong model sẽ tự hash
        if commit:
            instance.save()
        return instance


class HalinkUserPasswordForm(forms.ModelForm):
    """Form quản lý mật khẩu Thành viên - hiển thị field password riêng."""
    new_password = forms.CharField(
        label='Mật khẩu mới',
        widget=forms.PasswordInput(attrs={'placeholder': 'Để trống nếu không đổi'}),
        required=False,
        help_text='Nhập mật khẩu mới. Để trống nếu không thay đổi. Sẽ tự động hash md5(md5()) giống PHP cũ.'
    )

    class Meta:
        model = HalinkUser
        exclude = ['password']

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_pw = self.cleaned_data.get('new_password')
        if new_pw:
            instance.password = new_pw  # save() trong model sẽ tự hash
        if commit:
            instance.save()
        return instance


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


class FoodOrderProxyForm(forms.ModelForm):
    STATUS_CHOICES = [
        (1, 'Đang xử lý'),
        (0, 'Đã hoàn thành'),
        (3, 'Hủy/Lỗi'),
    ]
    ticlock = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-gray-950 dark:text-zinc-200 rounded-lg p-2 w-full focus:ring-1 focus:ring-primary-500 focus:outline-none'
        }),
        label="Trạng thái đơn hàng"
    )

    class Meta:
        model = FoodOrderProxy
        fields = '__all__'


class ProductAdminForm(forms.ModelForm):
    price = forms.IntegerField(label="Giá bán", required=False, min_value=0)
    promo_price = forms.IntegerField(label="Giá khuyến mãi", required=False, min_value=0)

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

# 1. Quản lý Admin
@admin.register(HalinkAdmin)
class HalinkAdminAdmin(ModelAdmin):
    form = HalinkAdminPasswordForm
    list_per_page = 20
    list_display = ('Id', 'username', 'fullname', 'email', 'level', 'time')
    search_fields = ('username', 'fullname', 'email')
    list_filter = ('level',)

# 2. Quản lý Thành viên
@admin.register(HalinkUser)
class HalinkUserAdmin(StatusSwitchAdminMixin, ModelAdmin):
    form = HalinkUserPasswordForm
    list_per_page = 20
    list_display = ('id', 'username', 'fullname', 'email', 'phone', 'date', 'ticlock')
    search_fields = ('username', 'fullname', 'email', 'phone')
    list_filter = ('ticlock', 'type_login', 'date')


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
                url = f"https://suoitien.vn/upload/flash/{obj.file_vn}"
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
# PROXY MODELS ADMINS
# ==============================================================================

@admin.register(PostProxy)
class PostProxyAdmin(JSONSchemaAdminMixin, SortableAdminMixin, StatusSwitchAdminMixin, CategoryAdminMixin, ImagePickerAdminMixin, SidebarAdminMixin, PostDisplayMixin, TinyMCEAdminMixin, MultiLangAdminMixin, ModelAdmin):
    category_type = 'postcat'  # Chuyên mục bài viết
    list_per_page = 20
    list_display = ('get_image', 'get_clean_title', 'get_category_display', 'display_sort_actions', 'get_hot_display', 'get_status_display', 'get_author_display', 'get_date_display')
    list_display_links = ('get_image', 'get_clean_title')
    search_fields = ('title_vn', 'content_vn', 'alias')
    list_filter = ('ticlock', 'date')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(post_type='post')

    def save_model(self, request, obj, form, change):
        import time
        if not change:
            obj.post_type = 'post'
            if not obj.date:  # PHP: date = time() khi tao moi
                obj.date = int(time.time())
        super().save_model(request, obj, form, change)


@admin.register(PostCategoryProxy)
class PostCategoryProxyAdmin(JSONSchemaAdminMixin, SortableAdminMixin, StatusSwitchAdminMixin, CategoryAdminMixin, ImagePickerAdminMixin, SidebarAdminMixin, PostDisplayMixin, TinyMCEAdminMixin, MultiLangAdminMixin, ModelAdmin):
    category_type = 'postcat'
    list_per_page = 20
    # Cột giống PHP: Ảnh, Tiêu đề, Nổi bật, Trạng thái, Tác giả, Thời gian
    list_display = ('get_image', 'get_clean_title', 'display_sort_actions', 'get_hot_display', 'get_status_display', 'get_author_display', 'get_date_display')
    list_display_links = ('get_image', 'get_clean_title')
    search_fields = ('title_vn', 'alias')
    list_filter = ('ticlock',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(post_type='postcat')

    def save_model(self, request, obj, form, change):
        import time
        if not change:
            obj.post_type = 'postcat'
            if not obj.date:
                obj.date = int(time.time())
        super().save_model(request, obj, form, change)


@admin.register(PageProxy)
class PageProxyAdmin(StatusSwitchAdminMixin, PostDisplayMixin, TinyMCEAdminMixin, MultiLangAdminMixin, ModelAdmin):
    list_display = ('Id', 'get_clean_title', 'alias', 'get_status_display', 'get_date_display')
    list_display_links = ('Id', 'get_clean_title')
    search_fields = ('title_vn', 'content_vn', 'alias')
    list_filter = ('ticlock',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(post_type='page')

    def save_model(self, request, obj, form, change):
        import time
        if not change:
            obj.post_type = 'page'
            if not obj.date:
                obj.date = int(time.time())
        super().save_model(request, obj, form, change)


@admin.register(ProductProxy)
class ProductProxyAdmin(JSONSchemaAdminMixin, SortableAdminMixin, StatusSwitchAdminMixin, CategoryAdminMixin, ImagePickerAdminMixin, SidebarAdminMixin, PostDisplayMixin, TinyMCEAdminMixin, MultiLangAdminMixin, ModelAdmin):
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
        import time
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
class ProductCategoryProxyAdmin(JSONSchemaAdminMixin, SortableAdminMixin, StatusSwitchAdminMixin, CategoryAdminMixin, ImagePickerAdminMixin, SidebarAdminMixin, PostDisplayMixin, TinyMCEAdminMixin, MultiLangAdminMixin, ModelAdmin):
    category_type = 'productcat'
    list_display = ('Id', 'get_clean_title', 'alias', 'display_sort_actions', 'get_status_display', 'get_date_display')
    list_display_links = ('Id', 'get_clean_title')
    search_fields = ('title_vn', 'alias')
    list_filter = ('ticlock',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(post_type='productcat')

    def save_model(self, request, obj, form, change):
        import time
        if not change:
            obj.post_type = 'productcat'
            if not obj.date:
                obj.date = int(time.time())
        super().save_model(request, obj, form, change)


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
        from .models import HalinkPost
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
            return mark_safe(html)
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
                        from .utils import send_email_via_smtp_proxy
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


@admin.register(FoodOrderProxy)
class FoodOrderProxyAdmin(ModelAdmin):
    form = FoodOrderProxyForm
    list_per_page = 20
    list_display = ('Id', 'get_order_id', 'get_fullname', 'get_phone', 'get_address', 'get_total_price', 'get_date', 'get_status')
    list_display_links = ('Id', 'get_order_id', 'get_fullname')
    search_fields = ('meta_value_cus', 'meta_like', 'Id_post')
    list_filter = ('ticlock', 'date')
    actions = ['resend_confirmation_email']
    readonly_fields = ('render_order_details',)
    
    fieldsets = (
        ('Bảng thông tin tổng hợp đơn đặt món', {
            'fields': ('render_order_details',),
        }),
        ('Trạng thái đơn đặt món', {
            'fields': ('ticlock',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(meta_type='order-food')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.meta_type = 'order-food'
            obj.meta_title = 'dat_mon_online'
            import time
            if not obj.Id_post:
                obj.Id_post = str(int(time.time()))
        super().save_model(request, obj, form, change)

    def _parse_food_products(self, meta_value):
        if not meta_value: return "---"
        import json
        try:
            items = json.loads(meta_value)
            if not isinstance(items, list):
                return f"<span style='color:red;'>Dữ liệu không phải là JSON array</span><br/>Raw: {html.escape(meta_value)}"
            
            html_str = ""
            total_all = 0
            from .models import HalinkPost
            for item in items:
                pid = item.get('id')
                qty = item.get('qtv') or item.get('qty') or 1
                price = item.get('price') or 0
                
                try:
                    qty = int(qty)
                except ValueError:
                    qty = 1
                try:
                    price = int(price)
                except ValueError:
                    price = 0
                
                post = HalinkPost.objects.filter(Id=pid).first()
                title = post.title_vn if post else f"Sản phẩm/Món ăn #{pid}"
                if title and '[[[:' in title:
                    from .utils import clean_lang
                    title = clean_lang(title)
                
                # Chống XSS
                title = html.escape(title)
                
                total = qty * price
                total_all += total
                html_str += f"<b>{title}</b><br/>Giá: {price:,} đ x {qty}<br/><br/>"
                
            html_str += f"<span style='color:#ef4444;font-weight:bold;font-size:16px;'>Tổng cộng: {total_all:,} đ</span>"
            return html_str
        except Exception as e:
            return f"<span style='color:red;'>Lỗi đọc sản phẩm: {str(e)}</span><br/>Raw: {html.escape(meta_value)}"

    def render_order_details(self, obj):
        try:
            prod_html = self._parse_food_products(obj.meta_value)
            
            # Đọc thông tin khách hàng từ JSON array
            customer_data = obj.get_customer_info()
            fullname = '---'
            phone = '---'
            address = '---'
            email = '---'
            time_ship = '---'
            payment = '---'
            note = '---'
            
            for item in customer_data:
                name = item.get('name')
                value = html.escape(str(item.get('value', '')))
                if name == 'fullname':
                    fullname = value
                elif name == 'phone':
                    phone = value
                elif name == 'address':
                    address = value
                elif name == 'email':
                    email = value
                elif name == 'time_ship':
                    time_ship = value
                elif name == 'payment':
                    payment = value
                elif name == 'note':
                    note = value

            dt = ""
            if obj.date:
                try:
                    from django.utils import timezone as tz
                    local_dt = tz.localtime(obj.date)
                    dt = local_dt.strftime('%d/%m/%Y %H:%M:%S')
                except Exception:
                    dt = str(obj.date)
                     
            payment_str = payment
            if payment == 'cod':
                payment_str = 'Tiền mặt khi nhận hàng (COD)'
            elif payment == 'banking':
                payment_str = 'Chuyển khoản ngân hàng'
            
            status_map = {0: 'Đã hoàn thành', 1: 'Đang xử lý', 3: 'Hủy/Lỗi'}
            status_str = status_map.get(obj.ticlock, f"Trạng thái {obj.ticlock}")
            
            if obj.ticlock == 0:
                status_html = f'<span style="color:#10b981; font-weight:bold;">✔ {status_str}</span>'
            elif obj.ticlock == 3:
                status_html = f'<span style="color:#ef4444; font-weight:bold;">✘ {status_str}</span>'
            else:
                status_html = f'<span style="color:#fbbf24; font-weight:bold;">● {status_str}</span>'
    
            html = f"""
            <div style="display: flex; gap: 20px; font-family: sans-serif; color:#ddd; font-size:14px; line-height:1.6;">
                <div style="flex: 1; background: #1a1a1a; padding: 20px; border-radius: 8px; border:1px solid #333;">
                    <h3 style="margin-top:0; border-bottom:1px solid #333; padding-bottom:10px; color:#fff;">Thông tin đơn đặt món</h3>
                    <p style="margin:5px 0;"><b>Mã đơn hàng (ID_post):</b> {obj.Id_post}</p>
                    <p style="margin:5px 0;"><b>Thời gian đặt:</b> {dt}</p>
                    <p style="margin:5px 0;"><b>Phương thức thanh toán:</b> {payment_str}</p>
                    <p style="margin:5px 0;"><b>Trạng thái:</b> {status_html}</p>
                    <br/>
                    <h3 style="margin-top:0; border-bottom:1px solid #333; padding-bottom:10px; color:#fff;">Món ăn đã chọn</h3>
                    <div>{prod_html}</div>
                </div>
                
                <div style="flex: 1; background: #1a1a1a; padding: 20px; border-radius: 8px; border:1px solid #333;">
                    <h3 style="margin-top:0; border-bottom:1px solid #333; padding-bottom:10px; color:#fff;">Thông tin giao hàng</h3>
                    <p style="margin:5px 0;"><b>Họ tên khách hàng:</b> {fullname}</p>
                    <p style="margin:5px 0;"><b>Số điện thoại:</b> {phone}</p>
                    <p style="margin:5px 0;"><b>Email:</b> {email}</p>
                    <p style="margin:5px 0;"><b>Địa chỉ giao hàng:</b> {address}</p>
                    <p style="margin:5px 0;"><b>Thời gian mong muốn nhận:</b> {time_ship}</p>
                    <p style="margin:5px 0;"><b>Ghi chú của khách:</b> {note}</p>
                </div>
            </div>
            """
            return mark_safe(html)
        except Exception as e:
            return f"Xảy ra lỗi khi hiển thị giao diện: {str(e)}"
    render_order_details.short_description = ' '

    def get_order_id(self, obj):
        return obj.Id_post or '---'
    get_order_id.short_description = 'Mã Đơn hàng (ID_post)'

    def get_fullname(self, obj):
        return obj.fullname or '---'
    get_fullname.short_description = 'Họ tên khách hàng'

    def get_phone(self, obj):
        return obj.phone or '---'
    get_phone.short_description = 'Số điện thoại'

    def get_address(self, obj):
        return obj.address or '---'
    get_address.short_description = 'Địa chỉ giao'

    def get_total_price(self, obj):
        if obj.meta_like:
            try:
                return f"{int(obj.meta_like):,} đ"
            except Exception:
                return f"{obj.meta_like} đ"
        return "0 đ"
    get_total_price.short_description = 'Tổng tiền'

    def get_date(self, obj):
        if obj.date:
            try:
                from django.utils import timezone as tz
                local_dt = tz.localtime(obj.date)
                return local_dt.strftime('%d/%m/%Y %H:%M')
            except Exception:
                return str(obj.date)
        return '---'
    get_date.short_description = 'Thời gian đặt'

    def get_status(self, obj):
        status_map = {0: 'Đã hoàn thành', 1: 'Đang xử lý', 3: 'Hủy/Lỗi'}
        status_str = status_map.get(obj.ticlock, f"Trạng thái {obj.ticlock}")
        
        if obj.ticlock == 0:
            return mark_safe(f'<span style="color:#10b981; font-weight:bold;">✔ {status_str}</span>')
        elif obj.ticlock == 3:
            return mark_safe(f'<span style="color:#ef4444; font-weight:bold;">✘ {status_str}</span>')
        else:
            return mark_safe(f'<span style="color:#fbbf24; font-weight:bold;">● {status_str}</span>')
    get_status.short_description = 'Trạng thái'

    def resend_confirmation_email(self, request, queryset):
        sent_count = 0
        error_count = 0
        for order in queryset:
            try:
                email = order.get_customer_field('email')
                fullname = html.escape(str(order.fullname or 'Quý khách'))
                
                if email and '@' in email:
                    from .utils import send_email_via_smtp_proxy
                    subject = f"Xác nhận đơn đặt món #{order.Id_post} - Suối Tiên Cuisine"
                    prod_html = self._parse_food_products(order.meta_value)
                    
                    # Định dạng tổng tiền
                    try:
                        total_formatted = f"{int(order.meta_like):,}"
                    except Exception:
                        total_formatted = str(order.meta_like)
                        
                    body_html = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <h2 style="color: #059669;">Kính gửi {fullname},</h2>
                        <p>Chúng tôi xin gửi lại thông tin xác nhận đơn đặt món ăn ẩm thực của quý khách tại Suối Tiên:</p>
                        <div style="background: #f3f4f6; padding: 15px; border-radius: 6px; margin: 15px 0;">
                            <p style="margin: 5px 0;"><b>Mã đơn hàng (ID_post):</b> {order.Id_post}</p>
                            <p style="margin: 5px 0;"><b>Thời gian đặt:</b> {order.date.strftime('%d/%m/%Y %H:%M:%S') if order.date else '---'}</p>
                            <p style="margin: 5px 0;"><b>Địa chỉ giao hàng:</b> {order.address or '---'}</p>
                            <p style="margin: 5px 0;"><b>Tổng cộng:</b> {total_formatted} đ</p>
                        </div>
                        <h3 style="border-bottom: 2px solid #059669; padding-bottom: 5px;">Món ăn đã đặt</h3>
                        <div style="margin-bottom: 20px;">{prod_html}</div>
                        <hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 20px 0;"/>
                        <p style="font-size: 12px; color: #6b7280;">Đây là thư tự động từ hệ thống ẩm thực Suối Tiên. Vui lòng không trả lời thư này.</p>
                    </body>
                    </html>
                    """
                    send_email_via_smtp_proxy(email.strip(), subject, body_html)
                    sent_count += 1
                else:
                    error_count += 1
            except Exception:
                error_count += 1
                
        self.message_user(
            request, 
            f"Đã gửi lại email xác nhận cho {sent_count} đơn đặt món." + 
            (f" Thất bại: {error_count} đơn đặt món do không có email hợp lệ hoặc lỗi kết nối." if error_count > 0 else "")
        )
    resend_confirmation_email.short_description = "Gửi lại email xác nhận đơn hàng"


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
