from django.contrib import admin
from unfold.admin import ModelAdmin

# Restrict default Django Admin access to superusers only (hide dev site from staff)
admin.site.has_permission = lambda request: request.user.is_active and request.user.is_superuser
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

class CleanTitleMixin:
    def get_clean_title(self, obj):
        return obj.clean_title
    get_clean_title.short_description = "Tiêu đề (VN)"

    def get_clean_diachi(self, obj):
        return obj.clean_diachi
    get_clean_diachi.short_description = "Địa chỉ"


# 1. Quản lý Admin
@admin.register(HalinkAdmin)
class HalinkAdminAdmin(ModelAdmin):
    list_per_page = 20
    list_display = ('Id', 'username', 'fullname', 'email', 'level', 'time')
    search_fields = ('username', 'fullname', 'email')
    list_filter = ('level',)

# 2. Quản lý Thành viên
@admin.register(HalinkUser)
class HalinkUserAdmin(ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'username', 'fullname', 'email', 'phone', 'date', 'ticlock')
    search_fields = ('username', 'fullname', 'email', 'phone')
    list_filter = ('ticlock', 'date')


# 4. Quản lý Banner & Quảng cáo
@admin.register(HalinkFlash)
class HalinkFlashAdmin(CleanTitleMixin, ModelAdmin):
    list_per_page = 20
    list_display = ('Id', 'get_clean_title', 'file_vn', 'link', 'ticlock')
    search_fields = ('title_vn', 'link')
    list_filter = ('ticlock',)

# 5. Quản lý Menu
@admin.register(HalinkMenu)
class HalinkMenuAdmin(CleanTitleMixin, ModelAdmin):
    list_per_page = 20
    list_display = ('Id', 'get_clean_title', 'id_cat', 'ticlock')
    search_fields = ('title_cat',)
    list_filter = ('ticlock',)

# 6. Cấu hình Website
@admin.register(HalinkWebsite)
class HalinkWebsiteAdmin(CleanTitleMixin, ModelAdmin):
    list_per_page = 20
    list_display = ('id', 'get_clean_title', 'hotline', 'email', 'get_clean_diachi')
    search_fields = ('title', 'email', 'hotline')

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
class PostProxyAdmin(CleanTitleMixin, ModelAdmin):
    list_per_page = 20
    list_display = ('Id', 'get_clean_title', 'alias', 'idcat', 'sort', 'ticlock', 'date')
    search_fields = ('title_vn', 'content_vn', 'alias')
    list_filter = ('ticlock', 'date')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(post_type='post')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.post_type = 'post'
        super().save_model(request, obj, form, change)


@admin.register(PostCategoryProxy)
class PostCategoryProxyAdmin(CleanTitleMixin, ModelAdmin):
    list_display = ('Id', 'get_clean_title', 'alias', 'sort', 'ticlock', 'date')
    search_fields = ('title_vn', 'alias')
    list_filter = ('ticlock',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(post_type='postcat')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.post_type = 'postcat'
        super().save_model(request, obj, form, change)


@admin.register(PageProxy)
class PageProxyAdmin(CleanTitleMixin, ModelAdmin):
    list_display = ('Id', 'get_clean_title', 'alias', 'ticlock', 'date')
    search_fields = ('title_vn', 'content_vn', 'alias')
    list_filter = ('ticlock',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(post_type='page')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.post_type = 'page'
        super().save_model(request, obj, form, change)


@admin.register(ProductProxy)
class ProductProxyAdmin(CleanTitleMixin, ModelAdmin):
    list_display = ('Id', 'get_clean_title', 'post_amount', 'idcat', 'sort', 'ticlock', 'date')
    search_fields = ('title_vn', 'description_vn', 'content_vn')
    list_filter = ('ticlock', 'date')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(post_type='product')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.post_type = 'product'
        super().save_model(request, obj, form, change)


@admin.register(ProductCategoryProxy)
class ProductCategoryProxyAdmin(CleanTitleMixin, ModelAdmin):
    list_display = ('Id', 'get_clean_title', 'alias', 'sort', 'ticlock', 'date')
    search_fields = ('title_vn', 'alias')
    list_filter = ('ticlock',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(post_type='productcat')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.post_type = 'productcat'
        super().save_model(request, obj, form, change)


@admin.register(TicketOrderProxy)
class TicketOrderProxyAdmin(ModelAdmin):
    list_per_page = 20
    list_display = ('Id', 'id_cart', 'total_price_final', 'date', 'status', 'ticlock')
    search_fields = ('id_cart', 'info_user')
    list_filter = ('status', 'date')


@admin.register(FoodOrderProxy)
class FoodOrderProxyAdmin(ModelAdmin):
    list_display = ('Id', 'Id_post', 'fullname', 'phone', 'address', 'total_price', 'date', 'ticlock')
    search_fields = ('meta_value_cus', 'meta_like')
    list_filter = ('ticlock', 'date')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(meta_type='order-food')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.meta_type = 'order-food'
            obj.meta_title = 'dat_mon_online'
        super().save_model(request, obj, form, change)


@admin.register(CommentProxy)
class CommentProxyAdmin(ModelAdmin):
    list_display = ('Id', 'Id_post', 'fullname', 'phone', 'content', 'star', 'date', 'ticlock')
    search_fields = ('meta_value',)
    list_filter = ('ticlock', 'date')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(meta_type='comment_post')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.meta_type = 'comment_post'
        super().save_model(request, obj, form, change)



@admin.register(SupportProxy)
class SupportProxyAdmin(ModelAdmin):
    list_display = ('Id', 'Id_post', 'meta_title', 'meta_value', 'date', 'ticlock')
    search_fields = ('meta_title', 'meta_value')
    list_filter = ('ticlock', 'date')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(meta_type='support')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.meta_type = 'support'
        super().save_model(request, obj, form, change)


@admin.register(LanguageProxy)
class LanguageProxyAdmin(ModelAdmin):
    list_display = ('Id', 'meta_title', 'meta_value', 'ticlock')
    search_fields = ('meta_title', 'meta_value')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(meta_type='halinklanguage')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.meta_type = 'halinklanguage'
        super().save_model(request, obj, form, change)


@admin.register(SMTPProxy)
class SMTPProxyAdmin(ModelAdmin):
    list_display = ('Id', 'meta_title', 'meta_value', 'ticlock')
    search_fields = ('meta_title', 'meta_value')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(meta_type='halinksmtp')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.meta_type = 'halinksmtp'
        super().save_model(request, obj, form, change)
