import hashlib
import json
import re

from django.core.exceptions import ValidationError
from django.db import models

def _is_md5_hash(value):
    """Kiểm tra xem giá trị đã là MD5 hash (32 ký tự hex) chưa."""
    if not value or len(value) != 32:
        return False
    return bool(re.match(r'^[a-fA-F0-9]{32}$', value))


def _md5_double_hash(plain_text):
    """Hash password theo chuẩn PHP cũ: md5(md5(password))."""
    first = hashlib.md5(plain_text.encode('utf-8')).hexdigest()
    return hashlib.md5(first.encode('utf-8')).hexdigest()


class HalinkAdmin(models.Model):
    Id = models.AutoField(primary_key=True, db_column='Id', verbose_name="ID")
    username = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tên tài khoản")
    password = models.CharField(max_length=255, null=True, blank=True, verbose_name="Mật khẩu")
    email = models.CharField(max_length=255, null=True, blank=True, verbose_name="Email")
    level = models.IntegerField(null=True, blank=True, verbose_name="Cấp độ")
    time = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian tạo")
    fullname = models.CharField(max_length=255, null=True, blank=True, verbose_name="Họ và tên")
    note = models.TextField(null=True, blank=True, verbose_name="Ghi chú")
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name="Địa chỉ")
    idcat = models.IntegerField(null=True, blank=True, verbose_name="Mã danh mục quản lý")

    class Meta:
        db_table = 'halink_admin'
        verbose_name = 'Tài khoản Admin'
        verbose_name_plural = 'Danh sách Admin'

    def __str__(self):
        return self.fullname or self.username or f"Admin #{self.Id}"

    def save(self, *args, **kwargs):
        # Hash password theo chuẩn PHP: md5(md5(password))
        if self.password:
            if self.pk:
                old_obj = type(self).objects.get(pk=self.pk)
                if old_obj.password != self.password:
                    self.password = _md5_double_hash(self.password)
            else:
                self.password = _md5_double_hash(self.password)
        super().save(*args, **kwargs)


class HalinkUser(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    username = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tên tài khoản")
    password = models.CharField(max_length=255, null=True, blank=True, verbose_name="Mật khẩu")
    email = models.CharField(max_length=255, null=True, blank=True, verbose_name="Email")
    fullname = models.CharField(max_length=255, null=True, blank=True, verbose_name="Họ và tên")
    birthday = models.TextField(null=True, blank=True, verbose_name="Ngày sinh")
    phone = models.CharField(max_length=255, null=True, blank=True, verbose_name="Số điện thoại")
    avatar = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ảnh đại diện")
    gioitinh = models.IntegerField(null=True, blank=True, verbose_name="Giới tính")
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name="Địa chỉ")
    date = models.DateField(null=True, blank=True, verbose_name="Ngày đăng ký")
    ticlock = models.IntegerField(default=0, verbose_name="Trạng thái khóa (Ẩn/Hiện)")
    type_login = models.CharField(max_length=11, null=True, blank=True, verbose_name="Hình thức đăng nhập")

    class Meta:
        db_table = 'halink_user'
        verbose_name = 'Thành viên'
        verbose_name_plural = 'Danh sách thành viên'

    def __str__(self):
        return self.fullname or self.username or f"Thành viên #{self.id}"

    def save(self, *args, **kwargs):
        # Hash password theo chuẩn PHP: md5(md5(password))
        if self.password:
            if self.pk:
                old_obj = type(self).objects.get(pk=self.pk)
                if old_obj.password != self.password:
                    self.password = _md5_double_hash(self.password)
            else:
                self.password = _md5_double_hash(self.password)
        super().save(*args, **kwargs)


class HalinkPost(models.Model):
    Id = models.AutoField(primary_key=True, db_column='Id')
    title_vn = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tiêu đề")
    alias = models.CharField(max_length=255, null=True, blank=True, verbose_name="Đường dẫn tĩnh")
    description_vn = models.TextField(null=True, blank=True, verbose_name="Mô tả ngắn")
    content_vn = models.TextField(null=True, blank=True, verbose_name="Nội dung chi tiết")
    post_type = models.CharField(max_length=255, null=True, blank=True, verbose_name="Loại bài viết")
    post_image = models.CharField(max_length=255, null=True, blank=True, verbose_name="Hình ảnh")
    post_gallery = models.TextField(null=True, blank=True, verbose_name="Bộ sưu tập ảnh")
    post_tags = models.CharField(max_length=255, null=True, blank=True, verbose_name="Từ khóa (Tags)")
    idcat = models.TextField(null=True, blank=True, verbose_name="Danh mục/Chuyên mục")
    sort = models.IntegerField(null=True, blank=True, verbose_name="Thứ tự sắp xếp")
    ticlock = models.CharField(max_length=1, default='0', verbose_name="Ẩn / Hiện")
    home = models.IntegerField(null=True, blank=True, verbose_name="Hiển thị trang chủ / Nổi bật")
    date = models.IntegerField(null=True, blank=True, verbose_name="Ngày đăng")
    meta_title = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tiêu đề SEO (Meta Title)")
    meta_keyword = models.CharField(max_length=255, null=True, blank=True, verbose_name="Từ khóa SEO (Meta Keyword)")
    meta_description = models.CharField(max_length=255, null=True, blank=True, verbose_name="Mô tả SEO (Meta Description)")
    id_user = models.IntegerField(default=1, verbose_name="ID người viết")
    post_amount = models.IntegerField(default=0, verbose_name="Giá bán/Số lượng")
    post_views = models.IntegerField(default=0, verbose_name="Lượt xem")
    post_type_show = models.IntegerField(null=True, blank=True, verbose_name="Loại hiển thị")
    post_sidebar = models.TextField(null=True, blank=True, verbose_name="Thanh bên (Sidebar)")
    post_banner = models.TextField(null=True, blank=True, verbose_name="Ảnh Banner")
    fullwidth = models.IntegerField(default=1, verbose_name="Hiển thị tràn màn hình (Fullwidth)")
    status = models.CharField(max_length=50, null=True, blank=True, verbose_name="Trạng thái")
    schema_org = models.TextField(null=True, blank=True, verbose_name="Cấu trúc Schema JSON-LD")

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

    def save(self, *args, **kwargs):
        # Tự động bọc ngôn ngữ cho tiêu đề, mô tả và nội dung nếu chưa có tag
        if self.title_vn and '[[[:' not in self.title_vn:
            self.title_vn = f"[[[:vi]]]{self.title_vn.strip()}[[[:end_vi]]]"
        if self.description_vn and '[[[:' not in self.description_vn:
            self.description_vn = f"[[[:vi]]]{self.description_vn.strip()}[[[:end_vi]]]"
        if self.content_vn and '[[[:' not in self.content_vn:
            self.content_vn = f"[[[:vi]]]{self.content_vn.strip()}[[[:end_vi]]]"
        super().save(*args, **kwargs)


class HalinkCart(models.Model):
    Id = models.AutoField(primary_key=True, db_column='Id', verbose_name="ID")
    id_cart = models.TextField(verbose_name="Mã đơn hàng")
    id_user = models.TextField(null=True, blank=True, verbose_name="ID người dùng")
    info_product = models.TextField(verbose_name="Thông tin vé đặt")
    info_user = models.TextField(verbose_name="Thông tin khách hàng")
    type_payment = models.IntegerField(verbose_name="Hình thức thanh toán")
    total_price = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tổng tiền gốc")
    voucher_code = models.CharField(max_length=255, null=True, blank=True, verbose_name="Mã giảm giá")
    discount_amount = models.CharField(max_length=255, null=True, blank=True, verbose_name="Số tiền giảm giá")
    total_price_final = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tổng tiền cuối cùng")
    dateoforg = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ngày tham quan")
    date = models.DateTimeField(verbose_name="Thời gian đặt")
    status = models.IntegerField(verbose_name="Trạng thái thanh toán")
    note = models.TextField(null=True, blank=True, verbose_name="Ghi chú nội bộ")
    note_for_user = models.TextField(null=True, blank=True, verbose_name="Ghi chú phản hồi cho khách")
    ticlock = models.IntegerField(verbose_name="Khóa đơn hàng")

    class Meta:
        db_table = 'halink_cart'
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Quản lý đơn hàng tổng hợp'

    @property
    def computed_total_price_num(self):
        # Ưu tiên lấy từ total_price_final nếu có số
        if self.total_price_final and self.total_price_final.strip() and self.total_price_final != '-':
            try:
                cleaned = ''.join(c for c in str(self.total_price_final) if c.isdigit())
                if cleaned:
                    return int(cleaned)
            except Exception:
                pass
        
        # Nếu không có, tính toán từ info_product (định dạng ID***+++***SL***+++***GIÁ)
        if self.info_product:
            try:
                total = 0
                items = [item.strip() for item in self.info_product.split(',') if item.strip()]
                for item in items:
                    parts = item.split('***+++***')
                    if len(parts) == 3:
                        sl = int(parts[1])
                        gia = int(parts[2])
                        total += sl * gia
                return total
            except Exception:
                pass
        return 0

    @property
    def computed_total_price_formatted(self):
        total = self.computed_total_price_num
        return f"{total:,}" if total > 0 else "0"

    def __str__(self):
        return f"Đơn hàng #{self.Id} - {self.computed_total_price_formatted} đ"

    def clean(self):
        # Validate info_product: mỗi item phải có đúng 3 phần ngăn cách bởi ***+++***
        if self.info_product:
            items = [item.strip() for item in self.info_product.split(',') if item.strip()]
            for idx, item in enumerate(items):
                parts = item.split('***+++***')
                if len(parts) != 3:
                    raise ValidationError({
                        'info_product': f'Mục thứ {idx+1} phải có đúng 3 phần '
                                        f'(ID***+++***SL***+++***GIÁ), '
                                        f'nhận được {len(parts)} phần: "{item}"'
                    })
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        # Chuẩn hóa khoảng trắng dư thừa trong info_product
        if self.info_product:
            items = [item.strip() for item in self.info_product.split(',') if item.strip()]
            self.info_product = ','.join(items)
        # Chuẩn hóa khoảng trắng trong info_user
        if self.info_user:
            self.info_user = self.info_user.strip()
        super().save(*args, **kwargs)



class HalinkFlash(models.Model):
    Id = models.AutoField(primary_key=True, db_column='Id', verbose_name="ID")
    file_vn = models.CharField(max_length=200, verbose_name="Tên file ảnh/banner")
    title_vn = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tiêu đề")
    link = models.CharField(max_length=200, verbose_name="Đường dẫn liên kết")
    width = models.CharField(max_length=100, verbose_name="Chiều rộng (px)")
    height = models.CharField(max_length=100, verbose_name="Chiều cao (px)")
    ticlock = models.IntegerField(null=True, blank=True, verbose_name="Ẩn/Hiện")
    description_vn = models.TextField(null=True, blank=True, verbose_name="Mô tả")
    date = models.IntegerField(null=True, blank=True, verbose_name="Thời gian")

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

    def save(self, *args, **kwargs):
        # Bọc tag ngôn ngữ cho title_vn (giống PHP flash/add.php)
        if self.title_vn and '[[[:' not in self.title_vn:
            self.title_vn = f"[[[:vi]]]{self.title_vn.strip()}[[[:end_vi]]]"
        # Bọc tag ngôn ngữ cho description_vn (giống PHP flash/edit.php)
        if self.description_vn and '[[[:' not in self.description_vn:
            self.description_vn = f"[[[:vi]]]{self.description_vn.strip()}[[[:end_vi]]]"
        super().save(*args, **kwargs)


class HalinkMenu(models.Model):
    Id = models.AutoField(primary_key=True, db_column='Id', verbose_name="ID")
    id_cat = models.IntegerField(null=True, blank=True, verbose_name="ID danh mục gốc")
    title_cat = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tiêu đề Menu")
    content_menu = models.TextField(null=True, blank=True, verbose_name="Nội dung/Liên kết Menu")
    ticlock = models.IntegerField(null=True, blank=True, verbose_name="Ẩn / Hiện")

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

    def save(self, *args, **kwargs):
        if self.title_cat and '[[[:' not in self.title_cat:
            self.title_cat = f"[[[:vi]]]{self.title_cat.strip()}[[[:end_vi]]]"
        super().save(*args, **kwargs)


class HalinkMeta(models.Model):
    Id = models.AutoField(primary_key=True, db_column='Id', verbose_name="ID")
    Id_post = models.IntegerField(null=True, blank=True, db_column='Id_post', verbose_name="Mã liên kết")
    meta_title = models.TextField(null=True, blank=True, verbose_name="Từ khóa Meta")
    meta_value = models.TextField(null=True, blank=True, verbose_name="Giá trị Meta (JSON/Nội dung)")
    meta_value_cus = models.TextField(null=True, blank=True, verbose_name="Thông tin khách hàng (JSON)")
    meta_type = models.CharField(max_length=255, null=True, blank=True, verbose_name="Loại Meta")
    meta_like = models.TextField(null=True, blank=True, verbose_name="Tổng tiền / Lượt thích")
    date = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian")
    ticlock = models.IntegerField(null=True, blank=True, verbose_name="Trạng thái khóa / Duyệt")

    class Meta:
        db_table = 'halink_meta'
        verbose_name = 'Dữ liệu Meta'
        verbose_name_plural = 'Dữ liệu Meta'

    def __str__(self):
        return f"Meta #{self.Id} (Post: {self.Id_post})"

    def clean(self):
        # Kiểm tra JSON hợp lệ cho order-food
        if self.meta_type == 'order-food':
            if self.meta_value:
                try:
                    data = json.loads(self.meta_value)
                    if not isinstance(data, list):
                        raise ValidationError({'meta_value': 'meta_value của order-food phải là một JSON array.'})
                except json.JSONDecodeError:
                    raise ValidationError({'meta_value': 'meta_value không phải JSON hợp lệ.'})
            if self.meta_value_cus:
                try:
                    data = json.loads(self.meta_value_cus)
                    if not isinstance(data, list):
                        raise ValidationError({'meta_value_cus': 'meta_value_cus của order-food phải là một JSON array.'})
                except json.JSONDecodeError:
                    raise ValidationError({'meta_value_cus': 'meta_value_cus không phải JSON hợp lệ.'})

        # Kiểm tra JSON hợp lệ cho comment_post
        elif self.meta_type == 'comment_post':
            if self.meta_value:
                try:
                    data = json.loads(self.meta_value)
                    if not isinstance(data, list):
                        raise ValidationError({'meta_value': 'meta_value của comment_post phải là một JSON array.'})
                except json.JSONDecodeError:
                    raise ValidationError({'meta_value': 'meta_value không phải JSON hợp lệ.'})
        super().clean()

    def save(self, *args, **kwargs):
        # Enforce giá trị mặc định cho các meta_type quan trọng (giống PHP request.php)
        if not self.pk:  # Chỉ khi tạo mới
            # comment_post và support: ticlock=1 (chờ duyệt) - PHP request.php:62,656
            if self.meta_type in ('comment_post', 'support') and self.ticlock is None:
                self.ticlock = 1
            # order-food: meta_title luôn là 'dat_mon_online' - PHP request.php:727
            if self.meta_type == 'order-food' and not self.meta_title:
                self.meta_title = 'dat_mon_online'

        # Tự động tính tổng tiền meta_like cho order-food (giống PHP request.php:738-744)
        if self.meta_type == 'order-food' and self.meta_value:
            try:
                items = json.loads(self.meta_value)
                if isinstance(items, list):
                    total = sum(
                        int(item.get('price', 0)) * int(item.get('qtv', 0))
                        for item in items if isinstance(item, dict)
                    )
                    if total > 0:
                        self.meta_like = str(total)
            except (json.JSONDecodeError, ValueError, TypeError):
                pass

        self.full_clean()
        super().save(*args, **kwargs)


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

    def save(self, *args, **kwargs):
        if self.title and '[[[:' not in self.title:
            self.title = f"[[[:vi]]]{self.title.strip()}[[[:end_vi]]]"
        if self.diachi and '[[[:' not in self.diachi:
            self.diachi = f"[[[:vi]]]{self.diachi.strip()}[[[:end_vi]]]"
        if self.tencty and '[[[:' not in self.tencty:
            self.tencty = f"[[[:vi]]]{self.tencty.strip()}[[[:end_vi]]]"
        if self.slogan and '[[[:' not in self.slogan:
            self.slogan = f"[[[:vi]]]{self.slogan.strip()}[[[:end_vi]]]"
        if self.message and '[[[:' not in self.message:
            self.message = f"[[[:vi]]]{self.message.strip()}[[[:end_vi]]]"
        if self.description and '[[[:' not in self.description:
            self.description = f"[[[:vi]]]{self.description.strip()}[[[:end_vi]]]"
        super().save(*args, **kwargs)


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



