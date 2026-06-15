import json
from .base import HalinkPost, HalinkCart, HalinkMeta

class PostProxy(HalinkPost):
    """
    Proxy Model đại diện cho Bài viết (post_type = 'post')
    """
    class Meta:
        proxy = True
        verbose_name = 'Bài viết'
        verbose_name_plural = 'Tất cả bài viết'


class PostCategoryProxy(HalinkPost):
    """
    Proxy Model đại diện cho Chuyên mục bài viết (post_type = 'postcat')
    """
    class Meta:
        proxy = True
        verbose_name = 'Chuyên mục bài viết'
        verbose_name_plural = 'Chuyên mục bài viết'


class PageProxy(HalinkPost):
    """
    Proxy Model đại diện cho Trang tĩnh (post_type = 'page')
    """
    class Meta:
        proxy = True
        verbose_name = 'Trang tĩnh'
        verbose_name_plural = 'Trang tĩnh'


class ProductProxy(HalinkPost):
    """
    Proxy Model đại diện cho Sản phẩm / Món ăn (post_type = 'product')
    """
    class Meta:
        proxy = True
        verbose_name = 'Sản phẩm/Món ăn'
        verbose_name_plural = 'Sản phẩm/Món ăn'


class ProductCategoryProxy(HalinkPost):
    """
    Proxy Model đại diện cho Chuyên mục sản phẩm (post_type = 'productcat')
    """
    class Meta:
        proxy = True
        verbose_name = 'Chuyên mục sản phẩm'
        verbose_name_plural = 'Chuyên mục sản phẩm'


class TicketOrderProxy(HalinkCart):
    """
    Proxy Model đại diện cho Đơn đặt vé vui chơi (cart_type = 'ticket')
    """
    class Meta:
        proxy = True
        verbose_name = 'Đơn hàng (Vé)'
        verbose_name_plural = 'Đơn hàng (Vé)'


class FoodOrderProxy(HalinkMeta):
    """
    Proxy Model đại diện cho Đơn đặt món ẩm thực (meta_type = 'order-food')
    """
    class Meta:
        proxy = True
        verbose_name = 'Đơn đặt món'
        verbose_name_plural = 'Đơn đặt món'

    def get_customer_info(self):
        try:
            return json.loads(self.meta_value_cus or '[]')
        except Exception:
            return []

    def get_customer_field(self, field_name):
        data = self.get_customer_info()
        for item in data:
            if item.get('name') == field_name:
                return item.get('value')
        return ""

    @property
    def fullname(self):
        return self.get_customer_field('fullname')

    @property
    def phone(self):
        return self.get_customer_field('phone')

    @property
    def address(self):
        return self.get_customer_field('address')

    @property
    def total_price(self):
        return self.meta_like


class SupportProxy(HalinkMeta):
    """
    Proxy Model đại diện cho Hỗ trợ & Góp ý (meta_type = 'support')
    """
    class Meta:
        proxy = True
        verbose_name = 'Hỗ trợ'
        verbose_name_plural = 'Hỗ trợ'


class CommentProxy(HalinkMeta):
    """
    Proxy Model đại diện cho Bình luận (meta_type = 'comment_post')
    """
    class Meta:
        proxy = True
        verbose_name = 'Bình luận'
        verbose_name_plural = 'Bình luận'

    def get_comment_data(self):
        try:
            return json.loads(self.meta_value or '[]')
        except Exception:
            return []

    def get_field_value(self, field_name):
        data = self.get_comment_data()
        for item in data:
            if item.get('name') == field_name:
                return item.get('value')
        return ""

    @property
    def fullname(self):
        return self.get_field_value('comment_name')

    @property
    def phone(self):
        return self.get_field_value('comment_phone')

    @property
    def content(self):
        return self.get_field_value('comment_content')

    @property
    def star(self):
        return self.get_field_value('comment_star')

    @property
    def processed_data(self):
        """
        Trả về dictionary đã bóc tách dữ liệu JSON và liên kết bài viết
        """
        data = self.get_comment_data()
        content = ""
        fullname = ""
        phone = ""
        star = 5
        images = []
        for item in data:
            name = item.get('name')
            val = item.get('value')
            if name == 'comment_content':
                content = val
            elif name == 'comment_name':
                fullname = val
            elif name == 'comment_phone':
                phone = val
            elif name == 'comment_star':
                try:
                    star = int(val) if val else 5
                except ValueError:
                    star = 5
            elif name == 'comment_img_rs':
                if val:
                    images = [img.strip() for img in val.split(',') if img.strip()]

        post = HalinkPost.objects.filter(Id=self.Id_post).first()
        post_title = post.title_vn if post else "Bài viết đã xóa"

        return {
            'Id': self.Id,
            'fullname': fullname or "Khách ẩn danh",
            'phone': phone,
            'content': content,
            'star': star,
            'images': images,
            'post_title': post_title,
            'reply': self.meta_value_cus if self.meta_value_cus != 'None' else '',
            'date': self.date,
            'ticlock': self.ticlock
        }


class LanguageProxy(HalinkMeta):
    """
    Proxy Model đại diện cho Ngôn ngữ (meta_type = 'halinklanguage')
    """
    class Meta:
        proxy = True
        verbose_name = 'Ngôn ngữ'
        verbose_name_plural = 'Ngôn ngữ'


class SMTPProxy(HalinkMeta):
    """
    Proxy Model đại diện cho Cấu hình SMTP (meta_type = 'halinksmtp')
    """
    class Meta:
        proxy = True
        verbose_name = 'Cấu hình SMTP'
        verbose_name_plural = 'Cấu hình SMTP'
