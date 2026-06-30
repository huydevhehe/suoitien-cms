import json
import random
import time

from rest_framework import serializers

from suoi_tien.models import (
    HalinkWebsite, HalinkFlash, HalinkPost, HalinkCart,
    TicketOrderProxy, FoodOrderProxy, CommentProxy, SupportProxy,
)
from suoi_tien.utils import build_media_url, clean_lang

SUPPORTED_LANGS = ('vi', 'en')


def get_request_lang(context):
    """Đọc ?lang=vi|en từ request trong serializer context, mặc định 'vi'."""
    request = context.get('request')
    lang = request.query_params.get('lang', 'vi') if request is not None else 'vi'
    return lang if lang in SUPPORTED_LANGS else 'vi'

PRODUCT_SEPARATOR = '***+++***'
USER_INFO_SEPARATOR = '***+++***'
GUEST_USER_INDEX = 'null'

# Trạng thái mặc định cho đơn mới do khách tự đặt (xem suoi_tien/admin/ticket_orders_admin.py, food_orders_admin.py).
ORDER_STATUS_UNPAID = 0
ORDER_LOCKED_PENDING_REVIEW = 1

# Nhãn trạng thái đơn hàng (đồng bộ map trong suoi_tien/admin/ticket_orders_admin.py).
ORDER_STATUS_LABELS = {
    0: 'Chưa thanh toán',
    1: 'Đang xử lý',
    3: 'Đã hủy',
    4: 'Thành công',
}


def get_order_status_label(status):
    return ORDER_STATUS_LABELS.get(status, 'Không xác định')


def parse_ticket_order_items(info_product):
    """
    Tách chuỗi info_product (ID***+++***SL***+++***GIÁ, cách nhau bằng dấu phẩy)
    thành danh sách item kèm tên sản phẩm tra từ HalinkPost. Dùng cho tra cứu đơn.
    """
    if not info_product:
        return []

    raw_items = []
    for line in info_product.split(','):
        parts = line.strip().split(PRODUCT_SEPARATOR)
        if len(parts) == 3:
            try:
                raw_items.append((int(parts[0]), int(parts[1]), int(parts[2])))
            except ValueError:
                continue

    titles = {
        post.Id: post.clean_title
        for post in HalinkPost.objects.filter(Id__in=[pid for pid, _, _ in raw_items])
    }
    return [
        {
            'post_id': pid,
            'title': titles.get(pid, 'Sản phẩm đã xóa'),
            'quantity': qty,
            'unit_price': price,
            'line_total': qty * price,
        }
        for pid, qty, price in raw_items
    ]


def generate_order_code(prefix):
    timestamp = int(time.time())
    random_suffix = random.randint(1000, 9999)
    return f"{prefix}{timestamp}{random_suffix}"


def resolve_ticket_items(items):
    """
    Validate danh sách {post_id, quantity} và tra giá thật từ HalinkPost.
    Giá luôn lấy từ DB (post_amount), không tin giá do client gửi lên.
    """
    if not items:
        raise serializers.ValidationError("Đơn hàng phải có ít nhất 1 sản phẩm.")

    post_ids = [item['post_id'] for item in items]
    products = HalinkPost.objects.filter(
        Id__in=post_ids, post_type='product', ticlock='0',
    )
    products_by_id = {product.Id: product for product in products}

    missing_ids = set(post_ids) - set(products_by_id.keys())
    if missing_ids:
        raise serializers.ValidationError(
            f"Sản phẩm không tồn tại hoặc đã ngừng bán: {sorted(missing_ids)}"
        )

    resolved_items = []
    for item in items:
        product = products_by_id[item['post_id']]
        resolved_items.append({
            'post_id': product.Id,
            'quantity': item['quantity'],
            'unit_price': product.post_amount,
        })
    return resolved_items


def build_ticket_order(*, fullname, phone, email='', address='', note='',
                        dateoforg, type_payment, resolved_items, id_user=None,
                        voucher_code=''):
    """
    Tạo và lưu 1 TicketOrderProxy từ danh sách item đã resolve giá (xem
    resolve_ticket_items). voucher_code chỉ lưu thô để Admin tự đối soát,
    KHÔNG tự tính giảm giá (chưa có bảng/quy tắc mã giảm giá).
    """
    from django.utils import timezone

    info_product = ','.join(
        PRODUCT_SEPARATOR.join([
            str(item['post_id']), str(item['quantity']), str(item['unit_price']),
        ])
        for item in resolved_items
    )
    info_user = USER_INFO_SEPARATOR.join([
        GUEST_USER_INDEX,
        fullname,
        phone,
        email,
        address,
        note,
    ])

    cart = TicketOrderProxy(
        id_cart=generate_order_code('DH'),
        id_user=id_user,
        info_product=info_product,
        info_user=info_user,
        type_payment=type_payment,
        voucher_code=voucher_code or None,
        dateoforg=dateoforg,
        date=timezone.now(),
        status=ORDER_STATUS_UNPAID,
        ticlock=ORDER_LOCKED_PENDING_REVIEW,
    )
    cart.save()
    return cart


class WebsiteSettingsSerializer(serializers.ModelSerializer):
    """
    Thông tin cấu hình website công khai: liên hệ, mạng xã hội, SEO, cờ hiển thị.
    Ẩn các field nhạy cảm: st_accesstoken, st_accesstoken_ex, theme.
    Hỗ trợ song ngữ qua ?lang=vi|en (mặc định vi, tự fallback nếu chưa dịch).
    """
    title = serializers.SerializerMethodField()
    slogan = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    favicon_url = serializers.SerializerMethodField()

    class Meta:
        model = HalinkWebsite
        fields = [
            'title', 'slogan', 'message', 'description', 'address', 'company_name',
            'keyword', 'email', 'hotline', 'hotline2', 'fanpage', 'youtube',
            'twitter', 'google', 'instagram', 'linkedin', 'googlemap',
            'opentime', 'closetime', 'logo_url', 'favicon_url',
            'googleanalytics', 'schema_home',
            'thugon_menu', 'active_chonve', 'enable', 'stamp',
        ]

    def get_title(self, obj) -> str:
        return clean_lang(obj.title, get_request_lang(self.context))

    def get_slogan(self, obj) -> str:
        return clean_lang(obj.slogan, get_request_lang(self.context))

    def get_message(self, obj) -> str:
        return clean_lang(obj.message, get_request_lang(self.context))

    def get_description(self, obj) -> str:
        return clean_lang(obj.description, get_request_lang(self.context))

    def get_address(self, obj) -> str:
        return clean_lang(obj.diachi, get_request_lang(self.context))

    def get_company_name(self, obj) -> str:
        return clean_lang(obj.tencty, get_request_lang(self.context))

    def get_logo_url(self, obj) -> str | None:
        return build_media_url(self.context.get('request'), obj.logo)

    def get_favicon_url(self, obj) -> str | None:
        return build_media_url(self.context.get('request'), obj.fav)


class BannerSerializer(serializers.ModelSerializer):
    """Hỗ trợ song ngữ qua ?lang=vi|en cho title/description."""
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = HalinkFlash
        fields = ['Id', 'title', 'description', 'image_url', 'link', 'width', 'height', 'date']

    def get_title(self, obj) -> str:
        return clean_lang(obj.title_vn, get_request_lang(self.context))

    def get_description(self, obj) -> str:
        return clean_lang(obj.description_vn, get_request_lang(self.context))

    def get_image_url(self, obj) -> str | None:
        return build_media_url(self.context.get('request'), obj.file_vn)


class MenuItemSerializer(serializers.Serializer):
    """Một mục trong cây menu đã được dựng từ `build_menu_tree` (xem menu_tree.py)."""
    type = serializers.CharField()
    title = serializers.CharField()
    url = serializers.CharField(allow_null=True)
    alias = serializers.CharField(allow_null=True)
    post_id = serializers.IntegerField(allow_null=True)
    children = serializers.ListField(child=serializers.DictField())


class MenuSerializer(serializers.Serializer):
    """Dùng để khai báo schema Swagger cho MenuListView — không gắn Model cụ thể."""
    Id = serializers.IntegerField()
    id_cat = serializers.IntegerField(allow_null=True)
    title = serializers.CharField()
    items = MenuItemSerializer(many=True)


class PostSummarySerializer(serializers.ModelSerializer):
    """Dữ liệu rút gọn dùng cho danh sách bài viết/trang/sản phẩm. Hỗ trợ ?lang=vi|en."""
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    product_subtype = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    promo_price = serializers.SerializerMethodField()
    price_child = serializers.SerializerMethodField()

    class Meta:
        model = HalinkPost
        fields = [
            'Id', 'title', 'alias', 'description', 'image_url', 'post_type',
            'post_amount', 'home', 'sort', 'date', 'post_views', 'idcat',
            'product_subtype', 'price', 'promo_price', 'price_child',
        ]

    def get_title(self, obj) -> str:
        return clean_lang(obj.title_vn, get_request_lang(self.context))

    def get_description(self, obj) -> str:
        return clean_lang(obj.description_vn, get_request_lang(self.context))

    def get_image_url(self, obj) -> str | None:
        return build_media_url(self.context.get('request'), obj.post_image)

    def get_product_subtype(self, obj) -> str | None:
        if obj.post_type != 'product':
            return None
        meta = HalinkMeta.objects.filter(Id_post=obj.pk, meta_title='product_subtype').first()
        return meta.meta_value if meta else 'ticket'

    def get_price(self, obj) -> int | None:
        if obj.post_type != 'product':
            return None
        meta = HalinkMeta.objects.filter(Id_post=obj.pk, meta_title='halink_metabox_gia').first()
        if meta and meta.meta_value:
            try:
                return int(meta.meta_value)
            except (ValueError, TypeError):
                pass
        return None

    def get_promo_price(self, obj) -> int | None:
        if obj.post_type != 'product':
            return None
        meta = HalinkMeta.objects.filter(Id_post=obj.pk, meta_title='halink_metabox_gia_khuyen_mai').first()
        if meta and meta.meta_value:
            try:
                return int(meta.meta_value)
            except (ValueError, TypeError):
                pass
        return None

    def get_price_child(self, obj) -> int | None:
        if obj.post_type != 'product':
            return None
        meta = HalinkMeta.objects.filter(Id_post=obj.pk, meta_title='price_child').first()
        if meta and meta.meta_value:
            try:
                return int(meta.meta_value)
            except (ValueError, TypeError):
                pass
        return None


class PostDetailSerializer(PostSummarySerializer):
    """Dữ liệu đầy đủ dùng cho trang chi tiết: nội dung, SEO, banner, cờ hiển thị."""
    content = serializers.SerializerMethodField()
    gallery_urls = serializers.SerializerMethodField()
    banner_url = serializers.SerializerMethodField()
    sidebar = serializers.CharField(source='post_sidebar', read_only=True)

    def get_content(self, obj) -> str:
        return clean_lang(obj.content_vn, get_request_lang(self.context))

    class Meta(PostSummarySerializer.Meta):
        fields = PostSummarySerializer.Meta.fields + [
            'content', 'gallery_urls', 'banner_url', 'sidebar', 'post_tags',
            'meta_title', 'meta_keyword', 'meta_description', 'schema_org',
            'fullwidth', 'status', 'post_type_show', 'id_user',
        ]

    def get_gallery_urls(self, obj) -> list[str]:
        if not obj.post_gallery:
            return []
        request = self.context.get('request')
        filenames = [name.strip() for name in obj.post_gallery.split(',') if name.strip()]
        return [build_media_url(request, name) for name in filenames]

    def get_banner_url(self, obj) -> str | None:
        return build_media_url(self.context.get('request'), obj.post_banner)


class CommentSerializer(serializers.Serializer):
    """Bình luận đã được duyệt, hiển thị công khai dưới bài viết/sản phẩm."""
    Id = serializers.IntegerField()
    fullname = serializers.CharField()
    content = serializers.CharField()
    star = serializers.IntegerField()
    images = serializers.ListField(child=serializers.CharField())
    reply = serializers.CharField(allow_blank=True)
    date = serializers.DateTimeField()

    @classmethod
    def from_proxy(cls, comment: CommentProxy):
        data = comment.processed_data
        return {
            'Id': data['Id'],
            'fullname': data['fullname'],
            'content': data['content'],
            'star': data['star'],
            'images': data['images'],
            'reply': data['reply'] or '',
            'date': data['date'],
        }


# ==================== GHI DỮ LIỆU (GUEST CHECKOUT) ====================

class TicketItemInputSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class TicketOrderCreateSerializer(serializers.Serializer):
    """
    Tạo đơn đặt vé dạng khách (không cần đăng nhập).
    Giá luôn được tính lại từ HalinkPost.post_amount, không tin giá do client gửi lên.
    """
    fullname = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=50)
    email = serializers.EmailField(required=False, allow_blank=True)
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    note = serializers.CharField(required=False, allow_blank=True, default='')
    dateoforg = serializers.CharField(max_length=255)
    type_payment = serializers.IntegerField(min_value=0, max_value=5)
    voucher_code = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')
    items = TicketItemInputSerializer(many=True)

    def validate_items(self, items):
        return resolve_ticket_items(items)

    def create(self, validated_data):
        return build_ticket_order(
            fullname=validated_data['fullname'],
            phone=validated_data['phone'],
            email=validated_data.get('email', ''),
            address=validated_data.get('address', ''),
            note=validated_data.get('note', ''),
            dateoforg=validated_data['dateoforg'],
            type_payment=validated_data['type_payment'],
            voucher_code=validated_data.get('voucher_code', ''),
            resolved_items=validated_data['items'],
        )


class TicketOrderLookupResultSerializer(serializers.Serializer):
    """Tra cứu đơn vé — trả đầy đủ thông tin đơn + danh sách item để FE hiển thị."""
    id_cart = serializers.CharField()
    date = serializers.DateTimeField()
    status = serializers.IntegerField()
    status_label = serializers.SerializerMethodField()
    total_price = serializers.CharField(source='computed_total_price_formatted')
    type_payment = serializers.IntegerField()
    dateoforg = serializers.CharField()
    voucher_code = serializers.CharField()
    note_for_user = serializers.CharField()
    fullname = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    def get_status_label(self, obj) -> str:
        return get_order_status_label(obj.status)

    def _info_user_parts(self, obj):
        return (obj.info_user or '').split(USER_INFO_SEPARATOR)

    def get_fullname(self, obj) -> str:
        parts = self._info_user_parts(obj)
        return parts[1] if len(parts) > 1 else ''

    def get_phone(self, obj) -> str:
        parts = self._info_user_parts(obj)
        return parts[2] if len(parts) > 2 else ''

    def get_items(self, obj) -> list:
        return parse_ticket_order_items(obj.info_product)


class FoodItemInputSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class FoodOrderCreateSerializer(serializers.Serializer):
    """Tạo đơn đặt món ăn dạng khách. Giá lấy từ DB, không tin client."""
    fullname = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=50)
    address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    items = FoodItemInputSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Đơn đặt món phải có ít nhất 1 món.")

        post_ids = [item['post_id'] for item in items]
        products = HalinkPost.objects.filter(
            Id__in=post_ids, post_type='product', ticlock='0',
        )
        products_by_id = {product.Id: product for product in products}

        missing_ids = set(post_ids) - set(products_by_id.keys())
        if missing_ids:
            raise serializers.ValidationError(
                f"Món ăn không tồn tại hoặc đã ngừng bán: {sorted(missing_ids)}"
            )

        resolved_items = []
        for item in items:
            product = products_by_id[item['post_id']]
            resolved_items.append({
                'name': product.clean_title,
                'price': product.post_amount,
                'qtv': item['quantity'],
            })
        return resolved_items

    def create(self, validated_data):
        from django.utils import timezone
        order = FoodOrderProxy(
            meta_type='order-food',
            meta_value=json.dumps(validated_data['items'], ensure_ascii=False),
            meta_value_cus=json.dumps([
                {'name': 'fullname', 'value': validated_data['fullname']},
                {'name': 'phone', 'value': validated_data['phone']},
                {'name': 'address', 'value': validated_data.get('address', '')},
            ], ensure_ascii=False),
            date=timezone.now(),
        )
        order.save()
        return order


class SupportCreateSerializer(serializers.Serializer):
    """Form Liên hệ / Góp ý công khai."""
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField()
    fullname = serializers.CharField(max_length=255, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=50, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    def create(self, validated_data):
        from django.utils import timezone
        support = SupportProxy(
            meta_type='support',
            meta_title=validated_data['subject'],
            meta_value=validated_data['message'],
            meta_value_cus=json.dumps([
                {'name': 'fullname', 'value': validated_data.get('fullname', '')},
                {'name': 'phone', 'value': validated_data.get('phone', '')},
                {'name': 'email', 'value': validated_data.get('email', '')},
            ], ensure_ascii=False),
            date=timezone.now(),
        )
        support.save()
        return support


class CommentCreateSerializer(serializers.Serializer):
    """Bình luận/đánh giá của khách dưới bài viết hoặc sản phẩm. Luôn chờ duyệt."""
    id_post = serializers.IntegerField(min_value=1)
    fullname = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=50, required=False, allow_blank=True)
    content = serializers.CharField()
    star = serializers.IntegerField(min_value=1, max_value=5, default=5)

    def validate_id_post(self, id_post):
        if not HalinkPost.objects.filter(Id=id_post, ticlock='0').exists():
            raise serializers.ValidationError("Bài viết/sản phẩm không tồn tại.")
        return id_post

    def create(self, validated_data):
        from django.utils import timezone
        comment = CommentProxy(
            Id_post=validated_data['id_post'],
            meta_type='comment_post',
            meta_value=json.dumps([
                {'name': 'comment_name', 'value': validated_data['fullname']},
                {'name': 'comment_phone', 'value': validated_data.get('phone', '')},
                {'name': 'comment_content', 'value': validated_data['content']},
                {'name': 'comment_star', 'value': str(validated_data['star'])},
            ], ensure_ascii=False),
            date=timezone.now(),
        )
        comment.save()
        return comment
