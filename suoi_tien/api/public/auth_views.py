from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from suoi_tien.models.proxies import TicketOrderProxy
from .auth_serializers import (
    CustomerRegisterSerializer, CustomerLoginSerializer, CustomerProfileSerializer,
    ChangePasswordSerializer, CustomerOrderHistorySerializer, TokenPairSerializer, MessageSerializer,
)
from .customer_auth import CustomerJWTAuthentication, IsCustomerAuthenticated, issue_customer_tokens
from .throttles import PublicAuthThrottle


class CustomerRegisterView(generics.CreateAPIView):
    """Đăng ký tài khoản khách hàng (giống /dang-ky của FE PHP cũ)."""
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [PublicAuthThrottle]
    serializer_class = CustomerRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {**issue_customer_tokens(user), 'message': 'Đăng ký thành công.'},
            status=status.HTTP_201_CREATED,
        )


class CustomerLoginView(APIView):
    """Đăng nhập khách hàng, trả về JWT riêng (không liên quan JWT Admin)."""
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [PublicAuthThrottle]

    @extend_schema(request=CustomerLoginSerializer, responses=TokenPairSerializer)
    def post(self, request):
        serializer = CustomerLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response(issue_customer_tokens(user))


class CustomerProfileView(generics.RetrieveUpdateAPIView):
    """Xem/sửa hồ sơ của chính khách hàng đang đăng nhập."""
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsCustomerAuthenticated]
    serializer_class = CustomerProfileSerializer

    def get_object(self):
        return self.request.user.halink_user


class ChangePasswordView(APIView):
    """Đổi mật khẩu của chính khách hàng đang đăng nhập."""
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsCustomerAuthenticated]
    throttle_classes = [PublicAuthThrottle]

    @extend_schema(request=ChangePasswordSerializer, responses=MessageSerializer)
    def post(self, request):
        user = request.user.halink_user
        serializer = ChangePasswordSerializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        user.password = serializer.validated_data['new_password']
        user.save()
        return Response({'message': 'Đổi mật khẩu thành công.'})


class CustomerOrderHistoryView(generics.ListAPIView):
    """Lịch sử đơn đặt vé của chính khách hàng đang đăng nhập."""
    authentication_classes = [CustomerJWTAuthentication]
    permission_classes = [IsCustomerAuthenticated]
    serializer_class = CustomerOrderHistorySerializer

    def get_queryset(self):
        customer = self.request.user.halink_user
        return TicketOrderProxy.objects.filter(id_user=str(customer.id)).order_by('-date')
