from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken

from suoi_tien.models import HalinkUser

# Tên claim riêng cho JWT khách hàng — KHÔNG dùng "user_id" (claim mà
# JWTAuthentication của Admin tìm) để 2 loại token không thể lẫn quyền nhau
# dù cùng chia sẻ SIGNING_KEY.
CUSTOMER_ID_CLAIM = 'customer_id'


class CustomerPrincipal:
    """Đại diện cho 1 khách hàng (HalinkUser) đã đăng nhập, dùng làm request.user."""
    is_authenticated = True
    is_anonymous = False
    is_staff = False

    def __init__(self, halink_user):
        self.halink_user = halink_user

    def __getattr__(self, name):
        return getattr(self.halink_user, name)


def issue_customer_tokens(user):
    refresh = RefreshToken()
    refresh[CUSTOMER_ID_CLAIM] = user.id
    access = refresh.access_token
    return {'access': str(access), 'refresh': str(refresh)}


class CustomerJWTAuthentication(JWTAuthentication):
    """JWT riêng cho khách hàng Public API — tách biệt hoàn toàn với JWT Admin CMS."""

    def get_user(self, validated_token):
        customer_id = validated_token.get(CUSTOMER_ID_CLAIM)
        if customer_id is None:
            raise InvalidToken("Token không hợp lệ cho khách hàng (thiếu customer_id).")

        try:
            halink_user = HalinkUser.objects.get(pk=customer_id)
        except HalinkUser.DoesNotExist:
            raise InvalidToken("Tài khoản không còn tồn tại.")

        if halink_user.ticlock:
            raise InvalidToken("Tài khoản đã bị khóa.")

        return CustomerPrincipal(halink_user)


class IsCustomerAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, CustomerPrincipal)


class CustomerJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """Khai báo riêng cho Swagger Public: JWT khách hàng khác JWT Admin."""
    target_class = CustomerJWTAuthentication
    name = 'CustomerBearerAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'JWT khách hàng (lấy từ /api/public/auth/login/) — khác với JWT Admin.',
        }
