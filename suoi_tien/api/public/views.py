from django.db.models import F, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from suoi_tien.models import HalinkWebsite, HalinkFlash, HalinkPost, HalinkMenu
from suoi_tien.models.proxies import CommentProxy, TicketOrderProxy
from suoi_tien.utils import clean_lang
from .menu_tree import build_menu_tree
from .serializers import (
    WebsiteSettingsSerializer, BannerSerializer, MenuSerializer,
    PostSummarySerializer, PostDetailSerializer, CommentSerializer,
    TicketOrderCreateSerializer, TicketOrderLookupResultSerializer,
    FoodOrderCreateSerializer, SupportCreateSerializer, CommentCreateSerializer,
    SUPPORTED_LANGS,
)
from .throttles import PublicWriteThrottle

WEBSITE_SETTINGS_PK = 1

DEFAULT_RELATED_LIMIT = 4
MAX_LIMIT = 50


def idcat_member_filter(category_id):
    """
    Trả về Q lọc bài có `category_id` là 1 phần tử trong chuỗi idcat (nối bằng
    dấu phẩy, không có phẩy đầu/cuối, vd '701,408,705'). Xét đủ 4 vị trí:
    đứng một mình / đầu / cuối / giữa — tránh lỗi cũ chỉ khớp ',X,'.
    """
    cid = str(category_id)
    return (
        Q(idcat=cid)
        | Q(idcat__startswith=f'{cid},')
        | Q(idcat__endswith=f',{cid}')
        | Q(idcat__contains=f',{cid},')
    )


def parse_limit(raw_limit, default=None):
    """Đọc query param limit, chặn trên MAX_LIMIT. Trả None nếu không hợp lệ/không có."""
    if raw_limit is None:
        return default
    try:
        value = int(raw_limit)
    except (TypeError, ValueError):
        return default
    if value <= 0:
        return default
    return min(value, MAX_LIMIT)


class PublicAPIMixin:
    """
    Mọi API Public đều mở cho khách vãng lai (không đăng nhập), nên KHÔNG gắn
    bất kỳ cơ chế xác thực nào (không JWT, không session) — tránh Swagger hiển
    thị nhầm icon khóa khiến người test tưởng phải có token mới gọi được.
    Việc sửa/xóa dữ liệu của người khác vẫn chỉ thực hiện được qua API Admin
    (IsAdminUser) — API Public chỉ có hành động đọc (GET) và tạo mới (POST).
    """
    authentication_classes = []
    permission_classes = [AllowAny]


class WebsiteSettingsView(PublicAPIMixin, generics.RetrieveAPIView):
    """Cấu hình chung của website: liên hệ, mạng xã hội, SEO trang chủ."""
    queryset = HalinkWebsite.objects.all()
    serializer_class = WebsiteSettingsSerializer

    def get_object(self):
        return generics.get_object_or_404(self.get_queryset(), pk=WEBSITE_SETTINGS_PK)


class MenuListView(PublicAPIMixin, APIView):
    """Trả về danh sách menu đã dựng sẵn dạng cây, sẵn sàng để FE render. Hỗ trợ ?lang=vi|en."""

    @extend_schema(
        parameters=[OpenApiParameter('lang', OpenApiTypes.STR, OpenApiParameter.QUERY,
                                      description="Ngôn ngữ hiển thị: vi hoặc en (mặc định vi).")],
        responses=MenuSerializer(many=True),
    )
    def get(self, request):
        lang = request.query_params.get('lang', 'vi')
        lang = lang if lang in SUPPORTED_LANGS else 'vi'

        menus = HalinkMenu.objects.filter(ticlock=0)
        data = [
            {
                'Id': menu.Id,
                'title': clean_lang(menu.title_cat, lang),
                'items': build_menu_tree(menu.content_menu, lang),
            }
            for menu in menus
        ]
        return Response(data)


class BannerListView(PublicAPIMixin, generics.ListAPIView):
    """Banner/Slideshow đang hiển thị (dùng cho trang chủ, combo khuyến mãi)."""
    queryset = HalinkFlash.objects.filter(ticlock=0)
    serializer_class = BannerSerializer


class WidgetSidebarView(PublicAPIMixin, APIView):
    """
    Đọc đúng các widget đang gắn ở 1 vị trí (sidebar) trong "Quản lý Widgets",
    theo đúng thứ tự admin đã sắp. Chỉ phục vụ các vị trí thật sự được theme đọc
    tới — đã rà soát trực tiếp source PHP gốc (xem widgets.py: VALID_POSITIONS).
    Hỗ trợ ?lang=vi|en.
    """

    @extend_schema(
        parameters=[OpenApiParameter('lang', OpenApiTypes.STR, OpenApiParameter.QUERY,
                                      description="Ngôn ngữ hiển thị: vi hoặc en (mặc định vi).")],
    )
    def get(self, request, position_id):
        from .widgets import resolve_sidebar_widgets

        lang = request.query_params.get('lang', 'vi')
        lang = lang if lang in SUPPORTED_LANGS else 'vi'

        result = resolve_sidebar_widgets(position_id, request, lang)
        if result is None:
            return Response({'detail': f'Vị trí "{position_id}" không tồn tại hoặc không được dùng.'}, status=404)
        return Response(result)


@extend_schema_view(
    list=extend_schema(parameters=[
        OpenApiParameter(
            'post_type', OpenApiTypes.STR, OpenApiParameter.QUERY,
            description="Lọc theo loại nội dung: post, page, product, postcat, productcat.",
        ),
        OpenApiParameter(
            'idcat', OpenApiTypes.STR, OpenApiParameter.QUERY,
            description="Lọc theo ID danh mục/chuyên mục.",
        ),
        OpenApiParameter(
            'limit', OpenApiTypes.INT, OpenApiParameter.QUERY,
            description=f"Giới hạn số bài trả về (tối đa {MAX_LIMIT}).",
        ),
        OpenApiParameter(
            'lang', OpenApiTypes.STR, OpenApiParameter.QUERY,
            description="Ngôn ngữ hiển thị title/description/content: vi hoặc en (mặc định vi).",
        ),
    ]),
    retrieve=extend_schema(parameters=[
        OpenApiParameter('lang', OpenApiTypes.STR, OpenApiParameter.QUERY,
                          description="Ngôn ngữ hiển thị: vi hoặc en (mặc định vi)."),
    ]),
)
class PostViewSet(PublicAPIMixin, viewsets.ReadOnlyModelViewSet):
    """
    Nội dung công khai: bài viết / trang tĩnh / sản phẩm / chuyên mục.
    Lọc theo `post_type` và `idcat`, tìm kiếm theo `search`, giới hạn `limit`.
    Tra chi tiết theo `alias` (slug) để FE có URL đẹp. Hỗ trợ song ngữ qua `?lang=vi|en`.
    """
    serializer_class = PostSummarySerializer
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
            queryset = queryset.filter(idcat_member_filter(category_id))

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        limit = parse_limit(request.query_params.get('limit'))
        if limit is not None:
            queryset = queryset[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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

    @action(detail=True, methods=['get'])
    @extend_schema(
        parameters=[
            OpenApiParameter(
                'limit', OpenApiTypes.INT, OpenApiParameter.QUERY,
                description=f"Số bài gợi ý (mặc định {DEFAULT_RELATED_LIMIT}, tối đa {MAX_LIMIT}).",
            ),
            OpenApiParameter(
                'lang', OpenApiTypes.STR, OpenApiParameter.QUERY,
                description="Ngôn ngữ hiển thị: vi hoặc en (mặc định vi).",
            ),
        ],
        responses=PostSummarySerializer(many=True),
    )
    def related(self, request, alias=None):
        """
        Bài/sản phẩm liên quan: cùng `post_type` + chia sẻ ít nhất 1 chuyên mục
        `idcat` với bài đang xem, loại bỏ chính nó. Nếu bài hiện tại không có
        chuyên mục → trả các bài mới nhất cùng `post_type`.
        """
        instance = self.get_object()
        limit = parse_limit(request.query_params.get('limit'), default=DEFAULT_RELATED_LIMIT)

        queryset = HalinkPost.objects.filter(
            ticlock='0', post_type=instance.post_type,
        ).exclude(pk=instance.pk)

        category_ids = [c.strip() for c in (instance.idcat or '').split(',') if c.strip()]
        if category_ids:
            cat_filter = Q()
            for cid in category_ids:
                cat_filter |= idcat_member_filter(cid)
            queryset = queryset.filter(cat_filter)

        queryset = queryset.order_by('-date')[:limit]
        serializer = PostSummarySerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class CommentListCreateView(PublicAPIMixin, generics.ListCreateAPIView):
    """
    GET: Bình luận/đánh giá ĐÃ DUYỆT của một bài viết hoặc sản phẩm (?id_post=).
    POST: Gửi bình luận mới dạng khách. Bình luận mới luôn ở trạng thái chờ duyệt.
    """

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


class _PublicWriteCreateView(PublicAPIMixin, generics.CreateAPIView):
    """Lớp cơ sở dùng chung cho mọi API ghi dữ liệu công khai (guest)."""
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


class TicketOrderLookupView(PublicAPIMixin, APIView):
    """Tra cứu đơn vé theo mã đơn + số điện thoại đã dùng để đặt."""

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


