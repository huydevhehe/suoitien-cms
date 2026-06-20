from django.db.models import F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import generics, status, viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from suoi_tien.models import HalinkWebsite, HalinkFlash, HalinkPost, HalinkMenu
from suoi_tien.models.proxies import CommentProxy, TicketOrderProxy
from .menu_tree import build_menu_tree
from .serializers import (
    WebsiteSettingsSerializer, BannerSerializer, MenuSerializer,
    PostSummarySerializer, PostDetailSerializer, CommentSerializer,
    TicketOrderCreateSerializer, TicketOrderLookupResultSerializer,
    FoodOrderCreateSerializer, SupportCreateSerializer, CommentCreateSerializer,
)
from .throttles import PublicWriteThrottle

WEBSITE_SETTINGS_PK = 1


class WebsiteSettingsView(generics.RetrieveAPIView):
    """Cấu hình chung của website: liên hệ, mạng xã hội, SEO trang chủ."""
    queryset = HalinkWebsite.objects.all()
    serializer_class = WebsiteSettingsSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        return generics.get_object_or_404(self.get_queryset(), pk=WEBSITE_SETTINGS_PK)


class MenuListView(APIView):
    """Trả về danh sách menu đã dựng sẵn dạng cây, sẵn sàng để FE render."""
    permission_classes = [AllowAny]

    @extend_schema(responses=MenuSerializer(many=True))
    def get(self, request):
        menus = HalinkMenu.objects.filter(ticlock=0)
        data = [
            {
                'Id': menu.Id,
                'title': menu.clean_title,
                'items': build_menu_tree(menu.content_menu),
            }
            for menu in menus
        ]
        return Response(data)


class BannerListView(generics.ListAPIView):
    """Banner/Slideshow đang hiển thị (dùng cho trang chủ, combo khuyến mãi)."""
    queryset = HalinkFlash.objects.filter(ticlock=0)
    serializer_class = BannerSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(parameters=[
        OpenApiParameter(
            'post_type', OpenApiTypes.STR, OpenApiParameter.QUERY,
            description="Lọc theo loại nội dung: post, page, product, postcat, productcat.",
        ),
        OpenApiParameter(
            'idcat', OpenApiTypes.STR, OpenApiParameter.QUERY,
            description="Lọc theo ID danh mục/chuyên mục cha.",
        ),
    ]),
)
class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Nội dung công khai: bài viết / trang tĩnh / sản phẩm / chuyên mục.
    Lọc theo `post_type` và `idcat`, tìm kiếm theo `search`.
    Tra chi tiết theo `alias` (slug) để FE có URL đẹp.
    """
    serializer_class = PostSummarySerializer
    permission_classes = [AllowAny]
    lookup_field = 'alias'
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title_vn', 'description_vn']
    ordering_fields = ['sort', 'date', 'post_views']

    def get_queryset(self):
        queryset = HalinkPost.objects.filter(ticlock='0').order_by('sort', '-date')

        post_type = self.request.query_params.get('post_type')
        if post_type:
            queryset = queryset.filter(post_type=post_type)

        category_id = self.request.query_params.get('idcat')
        if category_id:
            queryset = queryset.filter(idcat__contains=f',{category_id},')

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostSummarySerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        HalinkPost.objects.filter(pk=instance.pk).update(post_views=F('post_views') + 1)
        instance.refresh_from_db(fields=['post_views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CommentListCreateView(generics.ListCreateAPIView):
    """
    GET: Bình luận/đánh giá ĐÃ DUYỆT của một bài viết hoặc sản phẩm (?id_post=).
    POST: Gửi bình luận mới dạng khách. Bình luận mới luôn ở trạng thái chờ duyệt.
    """
    permission_classes = [AllowAny]

    def get_throttles(self):
        if self.request.method == 'POST':
            return [PublicWriteThrottle()]
        return super().get_throttles()

    def get_serializer_class(self):
        return CommentCreateSerializer if self.request.method == 'POST' else CommentSerializer

    def get_queryset(self):
        id_post = self.request.query_params.get('id_post')
        queryset = CommentProxy.objects.filter(meta_type='comment_post', ticlock=0)
        if id_post:
            queryset = queryset.filter(Id_post=id_post)
        return queryset.order_by('-date')

    def list(self, request, *args, **kwargs):
        comments = self.get_queryset()
        data = [CommentSerializer.from_proxy(comment) for comment in comments]
        return Response(CommentSerializer(data, many=True).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Gửi bình luận thành công, bình luận sẽ hiển thị sau khi được duyệt.'},
            status=status.HTTP_201_CREATED,
        )


class _PublicWriteCreateView(generics.CreateAPIView):
    """Lớp cơ sở dùng chung cho mọi API ghi dữ liệu công khai (guest)."""
    permission_classes = [AllowAny]
    throttle_classes = [PublicWriteThrottle]


class TicketOrderCreateView(_PublicWriteCreateView):
    """Đặt vé dạng khách (không cần đăng nhập). Giá tự tính lại từ DB."""
    serializer_class = TicketOrderCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            {
                'id_cart': order.id_cart,
                'total_price': order.computed_total_price_formatted,
                'message': 'Đặt vé thành công. Vui lòng lưu lại mã đơn để tra cứu.',
            },
            status=status.HTTP_201_CREATED,
        )


class TicketOrderLookupView(APIView):
    """Tra cứu đơn vé theo mã đơn + số điện thoại đã dùng để đặt."""
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter('id_cart', OpenApiTypes.STR, OpenApiParameter.QUERY, required=True),
            OpenApiParameter('phone', OpenApiTypes.STR, OpenApiParameter.QUERY, required=True),
        ],
        responses=TicketOrderLookupResultSerializer,
    )
    def get(self, request):
        id_cart = request.query_params.get('id_cart', '').strip()
        phone = request.query_params.get('phone', '').strip()
        if not id_cart or not phone:
            return Response(
                {'detail': 'Vui lòng cung cấp đủ id_cart và phone.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = TicketOrderProxy.objects.filter(id_cart=id_cart).first()
        if not order or phone not in (order.info_user or '').split('***+++***'):
            return Response(
                {'detail': 'Không tìm thấy đơn hàng khớp với thông tin đã cung cấp.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(TicketOrderLookupResultSerializer(order).data)


class FoodOrderCreateView(_PublicWriteCreateView):
    """Đặt món ăn dạng khách. Giá tự tính lại từ DB."""
    serializer_class = FoodOrderCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            {'Id': order.Id, 'total_price': order.total_price, 'message': 'Đặt món thành công.'},
            status=status.HTTP_201_CREATED,
        )


class SupportCreateView(_PublicWriteCreateView):
    """Gửi form Liên hệ / Góp ý."""
    serializer_class = SupportCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Gửi liên hệ thành công, chúng tôi sẽ phản hồi sớm nhất.'},
            status=status.HTTP_201_CREATED,
        )


