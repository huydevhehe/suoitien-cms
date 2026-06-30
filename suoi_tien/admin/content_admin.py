"""
Quản lý Nội dung: Bài viết, Chuyên mục bài viết, Trang tĩnh,
Sản phẩm, Chuyên mục sản phẩm.
"""
import time

from django.contrib import admin
from django import forms
from django.db.models import Subquery, OuterRef
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from ..models import (
    HalinkMeta,
    PostProxy,
    PostCategoryProxy,
    PageProxy,
    ProductProxy,
    ProductCategoryProxy,
)
from ..widgets import PriceInputWidget
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

# ==================== FORMS ====================

PRODUCT_SUBTYPE_CHOICES = [
    ('ticket', 'Vé / Combo'),
    ('food', 'Món ăn'),
]

class ProductAdminForm(forms.ModelForm):
    product_subtype = forms.ChoiceField(
        label="Loại sản phẩm",
        choices=PRODUCT_SUBTYPE_CHOICES,
        initial='ticket',
    )
    price = forms.IntegerField(
        label="Giá (người lớn)",
        required=False,
        min_value=0,
        widget=PriceInputWidget(),
    )
    promo_price = forms.IntegerField(
        label="Giá khuyến mãi",
        required=False,
        min_value=0,
        widget=PriceInputWidget(),
    )
    has_child_ticket = forms.BooleanField(
        label="Có giá vé trẻ em?",
        required=False,
    )
    price_child = forms.IntegerField(
        label="Giá vé trẻ em",
        required=False,
        min_value=0,
        widget=PriceInputWidget(),
    )

    class Meta:
        model = ProductProxy
        fields = [
            'title_vn', 'alias', 'description_vn', 'content_vn',
            'post_image', 'post_gallery', 'idcat', 'sort', 'ticlock', 'home'
        ]

    field_order = [
        'product_subtype', 'title_vn', 'alias', 'description_vn', 'content_vn',
        'price', 'promo_price', 'has_child_ticket', 'price_child',
        'post_image', 'post_gallery', 'idcat', 'sort', 'ticlock', 'home',
    ]

    class Media:
        js = ('admin/js/product_form.js',)

    def clean_title_vn(self):
        value = self.cleaned_data.get('title_vn')
        # MultiLangWidget trả về list [vi, en] hoặc string
        vi_val = value[0] if isinstance(value, (list, tuple)) else value
        if not vi_val or not str(vi_val).strip():
            raise forms.ValidationError('Tiêu đề tiếng Việt không được để trống.')
        return value

    def clean_alias(self):
        value = self.cleaned_data.get('alias', '')
        if not value or not str(value).strip():
            raise forms.ValidationError('URL (alias) không được để trống.')
        return value.strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            meta_map = {
                m.meta_title: m.meta_value
                for m in HalinkMeta.objects.filter(
                    Id_post=self.instance.pk,
                    meta_title__in=[
                        'halink_metabox_gia', 'halink_metabox_gia_khuyen_mai',
                        'product_subtype', 'price_child',
                    ]
                )
            }
            try:
                self.fields['price'].initial = int(meta_map['halink_metabox_gia'])
            except (KeyError, ValueError, TypeError):
                pass
            try:
                self.fields['promo_price'].initial = int(meta_map['halink_metabox_gia_khuyen_mai'])
            except (KeyError, ValueError, TypeError):
                pass
            if 'product_subtype' in meta_map:
                self.fields['product_subtype'].initial = meta_map['product_subtype']
            if 'price_child' in meta_map:
                try:
                    self.fields['price_child'].initial = int(meta_map['price_child'])
                    self.fields['has_child_ticket'].initial = True
                except (ValueError, TypeError):
                    pass


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
            if obj.sort is None:
                # Gán thứ tự cuối danh sách để mục mới có ngay nút di chuyển Lên/Xuống
                max_sort = self.model.objects.filter(post_type='post').exclude(sort__isnull=True).order_by('-sort').values_list('sort', flat=True).first()
                obj.sort = (max_sort or 0) + 1
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
    list_display_links = ('get_image', 'display_hierarchical_title')
    search_fields = ('title_vn', 'alias')
    list_filter = ('ticlock',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(post_type='postcat')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.post_type = 'postcat'
            if not obj.date:
                obj.date = int(time.time())
            if obj.sort is None:
                max_sort = self.model.objects.filter(post_type='postcat').exclude(sort__isnull=True).order_by('-sort').values_list('sort', flat=True).first()
                obj.sort = (max_sort or 0) + 1
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
class ProductProxyAdmin(JSONSchemaAdminMixin, SortableAdminMixin, StatusSwitchAdminMixin, CategoryAdminMixin, ImagePickerAdminMixin, UnixTimestampDateTimeAdminMixin, PostDisplayMixin, TinyMCEAdminMixin, MultiLangAdminMixin, ModelAdmin):
    category_type = 'productcat'  # Danh mục sản phẩm
    form = ProductAdminForm
    list_display = ('get_image', 'get_clean_title', 'get_price', 'get_category_display', 'display_sort_actions', 'get_status_display', 'get_date_display')
    list_display_links = ('get_image', 'get_clean_title')
    search_fields = ('title_vn', 'description_vn', 'content_vn')
    list_filter = ('ticlock', 'date')
    fieldsets = (
        (None, {'fields': ('product_subtype', 'title_vn', 'alias', 'content_vn', 'description_vn')}),
        ('Giá', {'fields': ('price', 'promo_price', 'has_child_ticket', 'price_child')}),
        ('Hình ảnh', {'fields': ('post_image', 'post_gallery')}),
        ('Cài đặt', {'fields': ('idcat', 'sort', 'ticlock', 'home')}),
    )

    def response_add(self, request, obj, post_url_continue=None):
        request.POST = request.POST.copy()
        request.POST['_continue'] = '1'
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        request.POST = request.POST.copy()
        request.POST['_continue'] = '1'
        return super().response_change(request, obj)

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
            if obj.sort is None:
                max_sort = self.model.objects.filter(post_type='product').exclude(sort__isnull=True).order_by('-sort').values_list('sort', flat=True).first()
                obj.sort = (max_sort or 0) + 1

        # post_amount la gia THAT duoc API public/dat ve-dat mon doc (xem serializers.py).
        # Truoc day form chi ghi gia vao HalinkMeta de hien thi danh sach Admin, khong dong
        # bo nguoc lai cot nay nen FE/khach hang luon thay gia = 0. Dong bo lai o day.
        price_val = form.cleaned_data.get('price')
        promo_val = form.cleaned_data.get('promo_price')
        if promo_val:
            obj.post_amount = promo_val
        elif price_val:
            obj.post_amount = price_val
        else:
            obj.post_amount = 0

        super().save_model(request, obj, form, change)

        from django.utils import timezone

        def _save_meta(key, value):
            if value is not None:
                meta, _ = HalinkMeta.objects.get_or_create(
                    Id_post=obj.pk, meta_title=key,
                    defaults={'meta_type': 'product', 'ticlock': 0, 'date': timezone.now()}
                )
                meta.meta_value = str(value)
                meta.save()

        _save_meta('halink_metabox_gia', price_val)
        _save_meta('halink_metabox_gia_khuyen_mai', promo_val)
        _save_meta('product_subtype', form.cleaned_data.get('product_subtype', 'ticket'))

        has_child = form.cleaned_data.get('has_child_ticket', False)
        price_child_val = form.cleaned_data.get('price_child') if has_child else None
        if price_child_val is not None:
            _save_meta('price_child', price_child_val)
        else:
            HalinkMeta.objects.filter(Id_post=obj.pk, meta_title='price_child').delete()


@admin.register(ProductCategoryProxy)
class ProductCategoryProxyAdmin(JSONSchemaAdminMixin, SortableAdminMixin, StatusSwitchAdminMixin, CategoryAdminMixin, ImagePickerAdminMixin, SidebarAdminMixin, UnixTimestampDateTimeAdminMixin, PostDisplayMixin, TinyMCEAdminMixin, MultiLangAdminMixin, ModelAdmin):
    category_type = 'productcat'
    fieldsets = (
        (None, {'fields': ('title_vn', 'alias', 'description_vn', 'content_vn')}),
        ('Hình ảnh', {'fields': ('post_image', 'post_banner')}),
        ('Cài đặt', {'fields': ('idcat', 'sort', 'ticlock', 'home')}),
        ('SEO', {'fields': ('meta_title', 'meta_description', 'schema_org')}),
    )

    def display_hierarchical_title(self, obj):
        if obj.idcat:
            return format_html('<span style="color: #a78bfa; font-weight: bold;">|— </span>{}', obj.clean_title)
        return obj.clean_title
    display_hierarchical_title.short_description = "Tiêu đề"

    list_display = ('get_image', 'display_hierarchical_title', 'alias', 'display_sort_actions', 'get_status_display', 'get_date_display')
    list_display_links = ('get_image', 'display_hierarchical_title')
    search_fields = ('title_vn', 'alias')
    list_filter = ('ticlock',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(post_type='productcat')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.post_type = 'productcat'
            if not obj.date:
                obj.date = int(time.time())
            if obj.sort is None:
                max_sort = self.model.objects.filter(post_type='productcat').exclude(sort__isnull=True).order_by('-sort').values_list('sort', flat=True).first()
                obj.sort = (max_sort or 0) + 1
        super().save_model(request, obj, form, change)
