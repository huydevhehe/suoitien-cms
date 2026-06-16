from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from .views import (
    HalinkAdminViewSet, HalinkUserViewSet, HalinkPostViewSet,
    TicketOrderViewSet, FoodOrderViewSet, CommentViewSet,
    SupportViewSet, HalinkMenuViewSet
)

# Sử dụng DefaultRouter để tự động hóa định tuyến RESTful CRUD
router = DefaultRouter()
router.register(r'admins', HalinkAdminViewSet, basename='admin')
router.register(r'users', HalinkUserViewSet, basename='user')
router.register(r'posts', HalinkPostViewSet, basename='post')
router.register(r'ticket-orders', TicketOrderViewSet, basename='ticket-order')
router.register(r'food-orders', FoodOrderViewSet, basename='food-order')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'supports', SupportViewSet, basename='support')
router.register(r'menus', HalinkMenuViewSet, basename='menu')

urlpatterns = [
    # Xác thực người dùng bằng JWT Token
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Tài liệu API tích hợp Swagger UI và Redoc
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Các CRUD endpoints chính của hệ thống
    path('', include(router.urls)),
]
