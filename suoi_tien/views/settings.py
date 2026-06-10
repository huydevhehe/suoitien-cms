from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

from ..models import HalinkMeta, HalinkWebsite, SMTPProxy, LanguageProxy

@login_required(login_url='admin_login')
def settings_view(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")
    tab = request.GET.get('tab', 'smtp')
    if tab not in ['smtp', 'lang', 'general']:
        tab = 'smtp'
        
    smtp_configs = SMTPProxy.objects.filter(meta_type='halinksmtp')
    lang_configs = LanguageProxy.objects.filter(meta_type='halinklanguage')
    website_config = HalinkWebsite.objects.first()
    
    if request.method == 'POST':
        # Handles quick updates of configuration values
        for config_id, value in request.POST.items():
            if config_id.startswith('config_'):
                cid = config_id.split('_')[1]
                meta = HalinkMeta.objects.filter(Id=cid).first()
                if meta:
                    meta.meta_value = value
                    meta.save()
            elif config_id.startswith('web_'):
                field_name = config_id[4:]
                if website_config and hasattr(website_config, field_name):
                    setattr(website_config, field_name, value)
                    
        if website_config:
            website_config.save()
            
        messages.success(request, "Cấu hình đã được lưu thành công.")
        return redirect(f"{request.path}?tab={tab}")
        
    context = {
        'smtp_configs': smtp_configs,
        'lang_configs': lang_configs,
        'website_config': website_config,
        'current_tab': tab,
        'active_menu': f'settings_{tab}'
    }
    return render(request, 'admin_fe/settings.html', context)
