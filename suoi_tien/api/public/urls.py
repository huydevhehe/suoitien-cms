from django.urls import path, include
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .views import (
    WebsiteSettingsView, MenuListView, BannerListView, PostViewSet,
    CommentListCreateView, TicketOrderCreateView, TicketOrderLookupView,
    FoodOrderCreateView, SupportCreateView, WidgetSidebarView,
    HomeSectionListView, HomeSectionDetailView,
)
from .page_sections import get_page_sections
from .auth_views import (
    CustomerRegisterView, CustomerLoginView, CustomerProfileView,
    ChangePasswordView, CustomerOrderHistoryView,
)

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='public-post')

# Swagger/Redoc riêng cho API Public: chỉ quét đúng các endpoint trong file này
# (không lẫn API Admin), ai cũng xem được (AllowAny) để FE/sếp test trực tiếp.
# SERVERS trỏ vào "/api/public/" để nút "Try it out" gọi đúng URL thật.
PUBLIC_SCHEMA_SETTINGS = {
    'TITLE': 'Suối Tiên - Public API (Frontend)',
    'DESCRIPTION': 'API công khai, không cần đăng nhập, dùng cho Frontend khách (suoitien.vercel.app).',
    'SERVERS': [{'url': '/api/public'}],
    'SECURITY': [],
}

urlpatterns = [
    path(
        'schema/',
        SpectacularAPIView.as_view(
            urlconf='suoi_tien.api.public.urls',
            permission_classes=[AllowAny],
            custom_settings=PUBLIC_SCHEMA_SETTINGS,
        ),
        name='public-schema',
    ),
    path(
        'schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='public-schema', permission_classes=[AllowAny]),
        name='public-swagger-ui',
    ),
    path(
        'schema/redoc/',
        SpectacularRedocView.as_view(url_name='public-schema', permission_classes=[AllowAny]),
        name='public-redoc',
    ),

    path('settings/', WebsiteSettingsView.as_view(), name='public-settings'),
    path('menus/', MenuListView.as_view(), name='public-menus'),
    path('banners/', BannerListView.as_view(), name='public-banners'),
    path('widgets/<str:position_id>/', WidgetSidebarView.as_view(), name='public-widget-sidebar'),
    path('home-sections/', HomeSectionListView.as_view(), name='public-home-sections'),
    path('home-sections/<str:section_key>/', HomeSectionDetailView.as_view(), name='public-home-section-detail'),
    path('page-sections/<str:page_key>/', get_page_sections, name='public-page-sections'),
    path('comments/', CommentListCreateView.as_view(), name='public-comments'),

    path('ticket-orders/', TicketOrderCreateView.as_view(), name='public-ticket-order-create'),
    path('ticket-orders/lookup/', TicketOrderLookupView.as_view(), name='public-ticket-order-lookup'),
    path('food-orders/', FoodOrderCreateView.as_view(), name='public-food-order-create'),
    path('supports/', SupportCreateView.as_view(), name='public-support-create'),

    # Đăng ký/đăng nhập khách hàng — JWT riêng, tách biệt hoàn toàn JWT Admin
    # (xem suoi_tien/api/public/customer_auth.py).
    path('auth/register/', CustomerRegisterView.as_view(), name='public-customer-register'),
    path('auth/login/', CustomerLoginView.as_view(), name='public-customer-login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='public-customer-token-refresh'),
    path('auth/profile/', CustomerProfileView.as_view(), name='public-customer-profile'),
    path('auth/profile/change-password/', ChangePasswordView.as_view(), name='public-customer-change-password'),
    path('auth/orders/', CustomerOrderHistoryView.as_view(), name='public-customer-orders'),

    path('', include(router.urls)),
]
