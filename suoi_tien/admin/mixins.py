"""
Mixins dùng chung cho các Admin class trong dự án Suối Tiên CMS.
Chứa các class hỗ trợ hiển thị, widget, sắp xếp dùng lại ở nhiều nơi.
"""
import datetime
import os

from django import forms
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin


class PostDisplayMixin:
    def get_clean_title(self, obj):
        return obj.clean_title
    get_clean_title.short_description = "Tiêu đề"

    def get_clean_diachi(self, obj):
        return obj.clean_diachi
    get_clean_diachi.short_description = "Địa chỉ"

    def get_image(self, obj):
        if obj.post_image:
            name = obj.post_image.split('/')[-1] if '/' in obj.post_image else obj.post_image
            
            # Thử đường dẫn gốc
            local_path = os.path.join(settings.MEDIA_ROOT, obj.post_image.lstrip('/'))
            url = f"{settings.MEDIA_URL}{obj.post_image.lstrip('/')}"
            
            # Nếu không thấy, thử tìm file nằm phẳng trong media/
            if not os.path.exists(local_path):
                fallback_path = os.path.join(settings.MEDIA_ROOT, name)
                if os.path.exists(fallback_path):
                    local_path = fallback_path
                    url = f"{settings.MEDIA_URL}{name}"

            if os.path.exists(local_path):
                return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:50%;" />', url)
            else:
                # Ảnh không tồn tại ở local → hiển thị placeholder SVG (không gọi mạng)
                placeholder = (
                    "data:image/svg+xml;utf8,"
                    "<svg xmlns='http://www.w3.org/2000/svg' width='40' height='40' viewBox='0 0 40 40'>"
                    "<rect width='40' height='40' rx='20' fill='%23e5e7eb'/>"
                    "<text x='50%25' y='54%25' text-anchor='middle' dominant-baseline='middle' "
                    "font-size='16' fill='%239ca3af'>?</text></svg>"
                )
                return format_html('<img src="{}" width="40" height="40" style="object-fit:cover; border-radius:50%;" />', placeholder)
        return ''
    get_image.short_description = 'Ảnh'

    def get_category_display(self, obj):
        if obj.idcat:
            try:
                cat_id = obj.idcat.strip(',').split(',')[0]
                from ..models import PostCategoryProxy, ProductCategoryProxy
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
            # ?v= để ép trình duyệt tải lại file mới mỗi khi sửa, tránh bị cache JS cũ
            # (đã gặp: sửa promotion:false xong nhưng browser vẫn hiện nút Upgrade do cache).
            'admin/js/tinymce_init.js?v=2',
        )


class MultiLangAdminMixin:
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in [
            'title_vn', 'title_cat', 'description_vn', 'content_vn',
            'title', 'diachi', 'tencty', 'slogan', 'message', 'description'
        ]:
            from django.db import models
            from ..widgets import MultiLangWidget
            widget_class = forms.Textarea if (isinstance(db_field, models.TextField) or db_field.name in ['message']) else forms.TextInput
            kwargs['widget'] = MultiLangWidget(widget_class=widget_class)
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class CategoryAdminMixin:
    """Mixin gắn CategoryCheckboxWidget vào field idcat."""
    category_type = 'postcat'  # Override trong từng admin class

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'idcat':
            from ..widgets import CategoryCheckboxWidget
            kwargs['widget'] = CategoryCheckboxWidget(category_type=self.category_type)
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'idcat' in form.base_fields:
            form.base_fields['idcat'].label = "Chuyên mục Cha"
            widget = form.base_fields['idcat'].widget
            # Truyền obj hiện tại vào widget để loại trừ khỏi danh sách (tránh Infinite Loop)
            if hasattr(widget, 'exclude_id'):
                widget.exclude_id = obj.Id if obj else None
        return form


class ImagePickerAdminMixin:
    """Mixin gắn ImagePickerWidget vào các field hình ảnh."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ['post_image', 'post_banner', 'logo', 'fav']:
            from ..widgets import ImagePickerWidget
            kwargs['widget'] = ImagePickerWidget(subfolder='hinhanh')
            return db_field.formfield(**kwargs)
        elif db_field.name == 'file_vn':
            from ..widgets import ImagePickerWidget
            kwargs['widget'] = ImagePickerWidget(subfolder='flash')
            return db_field.formfield(**kwargs)
        elif db_field.name == 'post_gallery':
            from ..widgets import GalleryPickerWidget
            kwargs['widget'] = GalleryPickerWidget(subfolder='hinhanh')
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class SidebarAdminMixin:
    """Mixin gắn SidebarCheckboxWidget vào field post_sidebar."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'post_sidebar':
            from ..widgets import SidebarCheckboxWidget
            kwargs['widget'] = SidebarCheckboxWidget()
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class StatusSwitchAdminMixin:
    """Mixin tự động áp dụng StatusSwitchWidget cho các trường trạng thái dạng 0/1 hoặc '0'/'1'."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ['ticlock', 'home', 'fullwidth', 'enable', 'thugon_menu']:
            from django.db import models
            from ..widgets import StatusSwitchWidget
            is_char = isinstance(db_field, (models.CharField, models.TextField))
            # ticlock bị ngược logic (0 = Duyệt/Hiện, 1 = Khóa/Ẩn)
            is_reversed = (db_field.name == 'ticlock')
            kwargs['widget'] = StatusSwitchWidget(is_char=is_char, reversed=is_reversed)
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class UnixTimestampDateTimeAdminMixin:
    """Mixin gắn UnixTimestampDateTimeWidget vào các trường lưu Unix Timestamp dạng số."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'date':
            from ..widgets import UnixTimestampDateTimeWidget
            kwargs['widget'] = UnixTimestampDateTimeWidget()
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class JSONSchemaAdminMixin:
    """Mixin tự động áp dụng JSONTextAreaWidget cho các trường Schema JSON-LD."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ['schema_org', 'schema_home']:
            from ..widgets import JSONTextAreaWidget
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
