from django.db import models

class HalinkAdmin(models.Model):
    Id = models.AutoField(primary_key=True, db_column='Id')
    username = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    level = models.IntegerField(null=True, blank=True)
    time = models.DateTimeField(null=True, blank=True)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    idcat = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'halink_admin'
        verbose_name = 'Tài khoản Admin'
        verbose_name_plural = 'Danh sách Admin'

    def __str__(self):
        return self.fullname or self.username or f"Admin #{self.Id}"


class HalinkUser(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    birthday = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.CharField(max_length=255, null=True, blank=True)
    gioitinh = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    ticlock = models.IntegerField(default=0)
    type_login = models.CharField(max_length=11, null=True, blank=True)

    class Meta:
        db_table = 'halink_user'
        verbose_name = 'Thành viên'
        verbose_name_plural = 'Danh sách thành viên'

    def __str__(self):
        return self.fullname or self.username or f"Thành viên #{self.id}"


class HalinkPost(models.Model):
    Id = models.AutoField(primary_key=True, db_column='Id')
    title_vn = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tiêu đề (VN)")
    alias = models.CharField(max_length=255, null=True, blank=True)
    description_vn = models.TextField(null=True, blank=True, verbose_name="Mô tả ngắn")
    content_vn = models.TextField(null=True, blank=True, verbose_name="Nội dung chi tiết")
    post_type = models.CharField(max_length=255, null=True, blank=True)
    post_image = models.CharField(max_length=255, null=True, blank=True, verbose_name="Hình ảnh")
    post_gallery = models.TextField(null=True, blank=True)
    post_tags = models.CharField(max_length=255, null=True, blank=True)
    idcat = models.TextField(null=True, blank=True)
    sort = models.IntegerField(null=True, blank=True)
    ticlock = models.CharField(max_length=1, default='0')
    home = models.IntegerField(null=True, blank=True)
    date = models.IntegerField(null=True, blank=True)
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_keyword = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.CharField(max_length=255, null=True, blank=True)
    id_user = models.IntegerField(default=1)
    post_amount = models.IntegerField(default=0, verbose_name="Giá bán/Số lượng")
    post_views = models.IntegerField(default=0)
    post_type_show = models.IntegerField(null=True, blank=True)
    post_sidebar = models.TextField(null=True, blank=True)
    post_banner = models.TextField(null=True, blank=True)
    fullwidth = models.IntegerField(default=1)
    status = models.CharField(max_length=50, null=True, blank=True)
    schema_org = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'halink_post'
        verbose_name = 'Nội dung (Bài viết/Trang/Sản phẩm)'
        verbose_name_plural = 'Quản lý Nội dung tổng hợp'

    @property
    def clean_title(self):
        from .utils import clean_lang
        return clean_lang(self.title_vn)

    @property
    def clean_description(self):
        from .utils import clean_lang
        return clean_lang(self.description_vn)

    @property
    def clean_content(self):
        from .utils import clean_lang
        return clean_lang(self.content_vn)

    def __str__(self):
        return self.clean_title or f"Nội dung #{self.Id}"


class HalinkCart(models.Model):
    Id = models.AutoField(primary_key=True, db_column='Id')
    id_cart = models.TextField()
    id_user = models.TextField(null=True, blank=True)
    info_product = models.TextField()
    info_user = models.TextField()
    type_payment = models.IntegerField()
    total_price = models.CharField(max_length=255, null=True, blank=True)
    voucher_code = models.CharField(max_length=255, null=True, blank=True)
    discount_amount = models.CharField(max_length=255, null=True, blank=True)
    total_price_final = models.CharField(max_length=255, null=True, blank=True)
    dateoforg = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField()
    status = models.IntegerField()
    note = models.TextField(null=True, blank=True)
    note_for_user = models.TextField(null=True, blank=True)
    ticlock = models.IntegerField()

    class Meta:
        db_table = 'halink_cart'
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Quản lý đơn hàng tổng hợp'

    def __str__(self):
        return f"Đơn hàng #{self.Id} - {self.total_price_final} đ"



class HalinkFlash(models.Model):
    Id = models.AutoField(primary_key=True, db_column='Id')
    file_vn = models.CharField(max_length=200, verbose_name="Tên file ảnh/banner")
    title_vn = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tiêu đề")
    link = models.CharField(max_length=200, verbose_name="Đường dẫn liên kết")
    width = models.CharField(max_length=100)
    height = models.CharField(max_length=100)
    ticlock = models.IntegerField(null=True, blank=True, verbose_name="Ẩn/Hiện")
    description_vn = models.TextField(null=True, blank=True, verbose_name="Mô tả")
    date = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'halink_flash'
        verbose_name = 'Banner & Quảng cáo'
        verbose_name_plural = 'Quản lý Banner/Quảng cáo'

    @property
    def clean_title(self):
        from .utils import clean_lang
        return clean_lang(self.title_vn)

    def __str__(self):
        return self.clean_title or f"Flash #{self.Id}"


class HalinkMenu(models.Model):
    Id = models.AutoField(primary_key=True, db_column='Id')
    id_cat = models.IntegerField(null=True, blank=True)
    title_cat = models.CharField(max_length=255, null=True, blank=True)
    content_menu = models.TextField(null=True, blank=True)
    ticlock = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'halink_menu'
        verbose_name = 'Cấu trúc Menu'
        verbose_name_plural = 'Quản lý Menu'

    @property
    def clean_title(self):
        from .utils import clean_lang
        return clean_lang(self.title_cat)

    def __str__(self):
        return self.clean_title or f"Menu #{self.Id}"


class HalinkMeta(models.Model):
    Id = models.AutoField(primary_key=True, db_column='Id')
    Id_post = models.IntegerField(null=True, blank=True, db_column='Id_post')
    meta_title = models.TextField(null=True, blank=True)
    meta_value = models.TextField(null=True, blank=True)
    meta_value_cus = models.TextField(null=True, blank=True)
    meta_type = models.CharField(max_length=255, null=True, blank=True)
    meta_like = models.TextField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    ticlock = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'halink_meta'
        verbose_name = 'Dữ liệu Meta'
        verbose_name_plural = 'Dữ liệu Meta'

    def __str__(self):
        return f"Meta #{self.Id} (Post: {self.Id_post})"


class HalinkMetabox(models.Model):
    Id = models.AutoField(primary_key=True, db_column='Id')
    meta_title = models.CharField(max_length=255)
    meta_key = models.CharField(max_length=255, null=True, blank=True)
    meta_type = models.CharField(max_length=255)
    post_type = models.CharField(max_length=255)
    ticlock = models.IntegerField()

    class Meta:
        db_table = 'halink_metabox'
        verbose_name = 'Metabox cấu hình'
        verbose_name_plural = 'Metabox cấu hình'

    def __str__(self):
        return self.meta_title


class HalinkStatistic(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.CharField(max_length=20)
    id_post = models.CharField(max_length=11)
    url = models.CharField(max_length=255)
    browser = models.CharField(max_length=20, null=True, blank=True)
    date = models.DateTimeField()

    class Meta:
        db_table = 'halink_statistic'
        verbose_name = 'Lịch sử truy cập'
        verbose_name_plural = 'Thống kê truy cập'

    def __str__(self):
        return f"IP: {self.ip} truy cập {self.url}"


class HalinkWebsite(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    keyword = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    slogan = models.CharField(max_length=255, null=True, blank=True)
    message = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    googleanalytics = models.TextField(null=True, blank=True)
    schema_home = models.TextField(null=True, blank=True)
    enable = models.IntegerField(null=True, blank=True)
    stamp = models.CharField(max_length=255, null=True, blank=True)
    hotline = models.CharField(max_length=255, null=True, blank=True)
    hotline2 = models.CharField(max_length=20, null=True, blank=True)
    fanpage = models.CharField(max_length=255, null=True, blank=True)
    youtube = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    google = models.CharField(max_length=255, null=True, blank=True)
    instagram = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    diachi = models.CharField(max_length=255, null=True, blank=True)
    tencty = models.CharField(max_length=255, null=True, blank=True)
    active_chonve = models.CharField(max_length=255)
    googlemap = models.TextField(null=True, blank=True)
    opentime = models.CharField(max_length=255, null=True, blank=True)
    closetime = models.CharField(max_length=255, null=True, blank=True)
    thugon_menu = models.IntegerField(null=True, blank=True)
    logo = models.CharField(max_length=255, null=True, blank=True)
    fav = models.CharField(max_length=255, null=True, blank=True)
    theme = models.TextField()
    st_accesstoken = models.TextField(null=True, blank=True)
    st_accesstoken_ex = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'halink_website'
        verbose_name = 'Cài đặt Website'
        verbose_name_plural = 'Cài đặt Website'

    @property
    def clean_title(self):
        from .utils import clean_lang
        return clean_lang(self.title)

    @property
    def clean_diachi(self):
        from .utils import clean_lang
        return clean_lang(self.diachi)

    @property
    def clean_tencty(self):
        from .utils import clean_lang
        return clean_lang(self.tencty)

    @property
    def clean_slogan(self):
        from .utils import clean_lang
        return clean_lang(self.slogan)

    @property
    def clean_message(self):
        from .utils import clean_lang
        return clean_lang(self.message)

    @property
    def clean_description(self):
        from .utils import clean_lang
        return clean_lang(self.description)

    def __str__(self):
        return self.clean_title or "Cấu hình Website"


# ==============================================================================
# PROXY MODELS: Tách giao diện Quản trị khớp với giao diện Web Admin gốc (Halink CMS)
# ==============================================================================

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
        import json
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
        import json
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



