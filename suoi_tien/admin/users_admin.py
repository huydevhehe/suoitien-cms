"""
Quản lý Tài khoản Admin CMS và Thành viên (HalinkAdmin, HalinkUser).
"""
from django.contrib import admin
from django import forms
from unfold.admin import ModelAdmin

from ..models import HalinkAdmin, HalinkUser
from .mixins import StatusSwitchAdminMixin


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
