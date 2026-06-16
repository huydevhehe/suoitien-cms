from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter

from suoi_tien.models import (
    HalinkAdmin, HalinkUser, HalinkPost, HalinkMenu,
    TicketOrderProxy, FoodOrderProxy, CommentProxy, SupportProxy
)
from .serializers import (
    HalinkAdminSerializer, HalinkUserSerializer, HalinkPostSerializer,
    TicketOrderSerializer, FoodOrderSerializer, CommentSerializer,
    SupportSerializer, HalinkMenuSerializer
)

class HalinkAdminViewSet(viewsets.ModelViewSet):
    """
    API Quản lý danh sách Tài khoản Admin.
    Yêu cầu Token JWT Admin.
    """
    queryset = HalinkAdmin.objects.all().order_by('-Id')
    serializer_class = HalinkAdminSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['username', 'fullname', 'email']
    ordering_fields = ['Id', 'time']


class HalinkUserViewSet(viewsets.ModelViewSet):
    """
    API Quản lý danh sách Thành viên.
    Yêu cầu Token JWT Admin.
    """
    queryset = HalinkUser.objects.all().order_by('-id')
    serializer_class = HalinkUserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['username', 'fullname', 'email', 'phone']
    ordering_fields = ['id', 'date']


class HalinkPostViewSet(viewsets.ModelViewSet):
    """
    API Quản lý Nội dung (Bài viết, Trang tĩnh, Sản phẩm, Món ăn).
    Lọc danh mục bằng query param ?post_type= (Ví dụ: 'post', 'page', 'product')
    Yêu cầu Token JWT Admin.
    """
    queryset = HalinkPost.objects.all().order_by('-Id')
    serializer_class = HalinkPostSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title_vn', 'alias', 'description_vn']
    ordering_fields = ['Id', 'sort', 'date', 'post_views']

    def get_queryset(self):
        queryset = super().get_queryset()
        post_type = self.request.query_params.get('post_type')
        if post_type:
            queryset = queryset.filter(post_type=post_type)
        return queryset


class TicketOrderViewSet(viewsets.ModelViewSet):
    """
    API Quản lý Đơn hàng Đặt vé.
    Yêu cầu Token JWT Admin.
    """
    queryset = TicketOrderProxy.objects.filter(id_cart__isnull=False).order_by('-Id')
    serializer_class = TicketOrderSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id_cart', 'info_user', 'voucher_code']
    ordering_fields = ['Id', 'date', 'status']


class FoodOrderViewSet(viewsets.ModelViewSet):
    """
    API Quản lý Đơn đặt món (Ẩm thực).
    Yêu cầu Token JWT Admin.
    """
    queryset = FoodOrderProxy.objects.filter(meta_type='order-food').order_by('-Id')
    serializer_class = FoodOrderSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['meta_title', 'meta_value', 'meta_value_cus']
    ordering_fields = ['Id', 'date', 'ticlock']


class CommentViewSet(viewsets.ModelViewSet):
    """
    API Quản lý Bình luận bài viết / Đánh giá.
    Yêu cầu Token JWT Admin.
    """
    queryset = CommentProxy.objects.filter(meta_type='comment_post').order_by('-Id')
    serializer_class = CommentSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ['Id', 'date', 'ticlock']


class SupportViewSet(viewsets.ModelViewSet):
    """
    API Quản lý Hỗ trợ & Ý kiến góp ý.
    Yêu cầu Token JWT Admin.
    """
    queryset = SupportProxy.objects.filter(meta_type='support').order_by('-Id')
    serializer_class = SupportSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [OrderingFilter]
    ordering_fields = ['Id', 'date', 'ticlock']


class HalinkMenuViewSet(viewsets.ModelViewSet):
    """
    API Quản lý Menu Website.
    Yêu cầu Token JWT Admin.
    """
    queryset = HalinkMenu.objects.all().order_by('Id')
    serializer_class = HalinkMenuSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title_cat']
    ordering_fields = ['Id']
