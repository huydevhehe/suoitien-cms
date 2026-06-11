"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from suoi_tien import views as suoi_tien_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Trang cấu hình giao diện & Widgets kéo thả
    path('admin/suoi_tien/themes/', admin.site.admin_view(suoi_tien_views.theme_info_view), name='admin_theme_info'),
    path('admin/suoi_tien/widgets/', admin.site.admin_view(suoi_tien_views.widgets_view), name='admin_widgets'),
    path('admin/suoi_tien/widgets/save/', admin.site.admin_view(suoi_tien_views.widgets_save_ajax), name='admin_widgets_save'),
    path('admin/suoi_tien/image-browser/', admin.site.admin_view(suoi_tien_views.image_browser_view), name='admin_image_browser'),

    # Tự động chuyển hướng trang chủ gốc vào trang Admin Unfold
    path('', RedirectView.as_view(url='/admin/', permanent=True)),
    
    # Django Admin gốc với giao diện Unfold
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

