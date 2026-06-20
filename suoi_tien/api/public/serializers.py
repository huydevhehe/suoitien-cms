import json
import random
import time

from rest_framework import serializers

from suoi_tien.models import (
    HalinkWebsite, HalinkFlash, HalinkPost, HalinkCart,
    TicketOrderProxy, FoodOrderProxy, CommentProxy, SupportProxy,
)
from suoi_tien.utils import build_media_url

PRODUCT_SEPARATOR = '***+++***'
USER_INFO_SEPARATOR = '***+++***'
GUEST_USER_INDEX = 'null'

# Trạng thái mặc định cho đơn mới do khách tự đặt (xem suoi_tien/admin/orders_admin.py).
ORDER_STATUS_UNPAID = 0
ORDER_LOCKED_PENDING_REVIEW = 1


def generate_order_code(prefix):
    timestamp = int(time.time())
    random_suffix = random.randint(1000, 9999)
    return f"{prefix}{timestamp}{random_suffix}"


class WebsiteSettingsSerializer(serializers.ModelSerializer):
    """
    Thông tin cấu hình website công khai: liên hệ, mạng xã hội, SEO.
    Không trả các field nội bộ (st_accesstoken, theme, active_chonve...).
    """
    title = serializers.CharField(source='clean_title', read_only=True)
    slogan = serializers.CharField(source='clean_slogan', read_only=True)
    message = serializers.CharField(source='clean_message', read_only=True)
    description = serializers.CharField(source='clean_description', read_only=True)
    address = serializers.CharField(source='clean_diachi', read_only=True)
    company_name = serializers.CharField(source='clean_tencty', read_only=True)
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
        ]

    def get_logo_url(self, obj) -> str | None:
        return build_media_url(self.context.get('request'), obj.logo)

    def get_favicon_url(self, obj) -> str | None:
        return build_media_url(self.context.get('request'), obj.fav)


class BannerSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='clean_title', read_only=True)
    description = serializers.CharField(source='description_vn', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = HalinkFlash
        fields = ['Id', 'title', 'description', 'image_url', 'link', 'width', 'height']

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
    title = serializers.CharField()
    items = MenuItemSerializer(many=True)


class PostSummarySerializer(serializers.ModelSerializer):
    """Dữ liệu rút gọn dùng cho danh sách bài viết/trang/sản phẩm."""
    title = serializers.CharField(source='clean_title', read_only=True)
    description = serializers.CharField(source='clean_description', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = HalinkPost
        fields = [
            'Id', 'title', 'alias', 'description', 'image_url', 'post_type',
            'post_amount', 'home', 'sort', 'date', 'post_views',
        ]

    def get_image_url(self, obj) -> str | None:
        return build_media_url(self.context.get('request'), obj.post_image)


class PostDetailSerializer(PostSummarySerializer):
    """Dữ liệu đầy đủ dùng cho trang chi tiết, gồm nội dung và SEO."""
    content = serializers.CharField(source='clean_content', read_only=True)
    gallery_urls = serializers.SerializerMethodField()

    class Meta(PostSummarySerializer.Meta):
        fields = PostSummarySerializer.Meta.fields + [
            'content', 'gallery_urls', 'idcat', 'post_tags',
            'meta_title', 'meta_keyword', 'meta_description', 'schema_org',
        ]

    def get_gallery_urls(self, obj) -> list[str]:
        if not obj.post_gallery:
            return []
        request = self.context.get('request')
        filenames = [name.strip() for name in obj.post_gallery.split(',') if name.strip()]
        return [build_media_url(request, name) for name in filenames]


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
    items = TicketItemInputSerializer(many=True)

    def validate_items(self, items):
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

    def create(self, validated_data):
        info_product = ','.join(
            PRODUCT_SEPARATOR.join([
                str(item['post_id']), str(item['quantity']), str(item['unit_price']),
            ])
            for item in validated_data['items']
        )
        info_user = USER_INFO_SEPARATOR.join([
            GUEST_USER_INDEX,
            validated_data['fullname'],
            validated_data['phone'],
            validated_data.get('email', ''),
            validated_data.get('address', ''),
            validated_data.get('note', ''),
        ])

        from django.utils import timezone
        cart = TicketOrderProxy(
            id_cart=generate_order_code('DH'),
            info_product=info_product,
            info_user=info_user,
            type_payment=validated_data['type_payment'],
            dateoforg=validated_data['dateoforg'],
            date=timezone.now(),
            status=ORDER_STATUS_UNPAID,
            ticlock=ORDER_LOCKED_PENDING_REVIEW,
        )
        cart.save()
        return cart


class TicketOrderLookupResultSerializer(serializers.Serializer):
    id_cart = serializers.CharField()
    date = serializers.DateTimeField()
    status = serializers.IntegerField()
    total_price = serializers.CharField(source='computed_total_price_formatted')


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
