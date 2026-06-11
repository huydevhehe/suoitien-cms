import hashlib
import json

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from suoi_tien.models import (
    HalinkAdmin, HalinkCart, HalinkFlash, HalinkMenu, HalinkMeta,
    HalinkPost, HalinkUser, HalinkWebsite,
    _is_md5_hash, _md5_double_hash,
)


class DataParityTestCase(TestCase):
    """
    Bộ kiểm thử Data Parity toàn diện.
    Đảm bảo Django ghi dữ liệu xuống DB giống hệt PHP CMS cũ.
    Tham chiếu: request.php, flash/add.php, flash/edit.php,
                user/add.php, thanhvien/add.php, website/edit.php
    """

    # ================================================================
    # 1-2. HalinkPost: Bọc tag ngôn ngữ [[[:vi]]]
    # PHP: Tất cả nội dung text đều bọc tag đa ngôn ngữ
    # ================================================================

    def test_post_language_wrapping(self):
        """Bài viết mới phải tự động bọc tag [[[:vi]]]."""
        post = HalinkPost(
            title_vn="Tin tức mới 2026",
            description_vn="Mô tả tin tức mới",
            content_vn="Nội dung tin tức mới",
        )
        post.save()
        self.assertEqual(post.title_vn, "[[[:vi]]]Tin tức mới 2026[[[:end_vi]]]")
        self.assertEqual(post.description_vn, "[[[:vi]]]Mô tả tin tức mới[[[:end_vi]]]")
        self.assertEqual(post.content_vn, "[[[:vi]]]Nội dung tin tức mới[[[:end_vi]]]")

    def test_post_no_double_wrapping(self):
        """Bài viết đã có tag không được bọc trùng."""
        post = HalinkPost(
            title_vn="[[[:vi]]]Tin tức có sẵn[[[:end_vi]]]",
            description_vn="[[[:vi]]]Mô tả có sẵn[[[:end_vi]]]",
            content_vn="[[[:vi]]]Nội dung có sẵn[[[:end_vi]]]",
        )
        post.save()
        self.assertEqual(post.title_vn, "[[[:vi]]]Tin tức có sẵn[[[:end_vi]]]")
        self.assertEqual(post.description_vn, "[[[:vi]]]Mô tả có sẵn[[[:end_vi]]]")
        self.assertEqual(post.content_vn, "[[[:vi]]]Nội dung có sẵn[[[:end_vi]]]")

    # ================================================================
    # 3-4. HalinkCart: Format info_product ***+++***
    # PHP request.php:471 → implode('***+++***', array(id, qty, price))
    # ================================================================

    def test_cart_whitespace_cleanup(self):
        """Đơn vé phải strip khoảng trắng thừa trong info_product và info_user."""
        cart = HalinkCart(
            id_cart="123456789",
            info_product=" 6517***+++***2***+++***360000 , 6518***+++***1***+++***232000 ",
            info_user=" null***+++***Nguyen Van A***+++***0123456789***+++***a@gmail.com***+++***Ha Noi***+++*** ",
            type_payment=2,
            status=1,
            ticlock=0,
            date=timezone.now(),
        )
        cart.save()
        self.assertEqual(
            cart.info_product,
            "6517***+++***2***+++***360000,6518***+++***1***+++***232000",
        )
        self.assertEqual(
            cart.info_user,
            "null***+++***Nguyen Van A***+++***0123456789***+++***a@gmail.com***+++***Ha Noi***+++***",
        )

    def test_cart_invalid_info_product_format(self):
        """info_product sai format (không đủ 3 phần) phải bị reject."""
        cart = HalinkCart(
            id_cart="999999999",
            info_product="6517***+++***2",  # Chỉ có 2 phần, thiếu price
            info_user="null***+++***Test",
            type_payment=1,
            status=0,
            ticlock=0,
            date=timezone.now(),
        )
        with self.assertRaises(ValidationError):
            cart.save()

    # ================================================================
    # 5-7. HalinkMeta: order-food JSON validation + defaults
    # PHP request.php:726-746
    # ================================================================

    def test_meta_food_order_json_validation(self):
        """order-food: meta_value phải là JSON array, không phải object."""
        meta = HalinkMeta(
            meta_type="order-food",
            meta_value='{"id": 6517, "qtv": 2, "price": 360000}',
            meta_value_cus='[{"name": "fullname", "value": "A"}]',
        )
        with self.assertRaises(ValidationError):
            meta.save()

    def test_meta_food_order_auto_total(self):
        """order-food: meta_like phải tự động tính tổng tiền (giống PHP request.php:738-744)."""
        meta = HalinkMeta(
            meta_type="order-food",
            meta_value='[{"id": "100", "qtv": 2, "price": 50000}, {"id": "101", "qtv": 3, "price": 30000}]',
            meta_value_cus='[{"name": "fullname", "value": "Nguyen Van A"}]',
        )
        meta.save()
        # 2*50000 + 3*30000 = 190000
        self.assertEqual(meta.meta_like, "190000")

    def test_meta_food_order_defaults(self):
        """order-food mới: meta_title = 'dat_mon_online' (giống PHP request.php:727)."""
        meta = HalinkMeta(
            meta_type="order-food",
            meta_value='[{"id": "100", "qtv": 1, "price": 50000}]',
            meta_value_cus='[{"name": "fullname", "value": "Test"}]',
        )
        meta.save()
        self.assertEqual(meta.meta_title, "dat_mon_online")

    # ================================================================
    # 8-9. HalinkMeta: comment_post + support defaults
    # PHP request.php:656 → ticlock = 1 (chờ duyệt)
    # PHP request.php:62 → ticlock = 1
    # ================================================================

    def test_meta_comment_validation(self):
        """comment_post: meta_value phải là JSON array."""
        meta = HalinkMeta(
            meta_type="comment_post",
            meta_value='{"name": "fullname", "value": "A"}',
        )
        with self.assertRaises(ValidationError):
            meta.save()

    def test_meta_comment_default_ticlock(self):
        """comment_post mới: ticlock = 1 (chờ duyệt, giống PHP request.php:656)."""
        meta = HalinkMeta(
            meta_type="comment_post",
            meta_value='[{"name": "comment_name", "value": "Test"}]',
        )
        meta.save()
        self.assertEqual(meta.ticlock, 1)

    def test_meta_support_default_ticlock(self):
        """support mới: ticlock = 1 (chờ xử lý, giống PHP request.php:62)."""
        meta = HalinkMeta(
            meta_type="support",
            meta_title="Góp ý dịch vụ",
            meta_value="Nội dung góp ý",
        )
        meta.save()
        self.assertEqual(meta.ticlock, 1)

    # ================================================================
    # 10-11. HalinkFlash: Bọc tag cho cả title_vn và description_vn
    # PHP flash/add.php → title_vn
    # PHP flash/edit.php:19 → description_vn
    # ================================================================

    def test_flash_title_language_wrapping(self):
        """Banner: title_vn phải bọc tag [[[:vi]]]."""
        flash = HalinkFlash(
            file_vn="test.jpg",
            title_vn="Banner Test",
            link="/test",
            width="100",
            height="100",
        )
        flash.save()
        self.assertEqual(flash.title_vn, "[[[:vi]]]Banner Test[[[:end_vi]]]")

    def test_flash_description_language_wrapping(self):
        """Banner: description_vn phải bọc tag [[[:vi]]] (giống PHP flash/edit.php:19)."""
        flash = HalinkFlash(
            file_vn="test.jpg",
            title_vn="Banner Test",
            description_vn="Mô tả banner đẹp",
            link="/test",
            width="100",
            height="100",
        )
        flash.save()
        self.assertEqual(flash.description_vn, "[[[:vi]]]Mô tả banner đẹp[[[:end_vi]]]")

    # ================================================================
    # 12. HalinkMenu: Bọc tag cho title_cat
    # ================================================================

    def test_menu_language_wrapping(self):
        """Menu: title_cat phải bọc tag [[[:vi]]]."""
        menu = HalinkMenu(title_cat="Trang chủ")
        menu.save()
        self.assertEqual(menu.title_cat, "[[[:vi]]]Trang chủ[[[:end_vi]]]")

    # ================================================================
    # 13. HalinkWebsite: Bọc tag cho tất cả trường text
    # PHP website/edit.php → title, diachi, tencty, slogan, message, description
    # ================================================================

    def test_website_language_wrapping(self):
        """Website: Tất cả trường text phải bọc tag [[[:vi]]]."""
        web = HalinkWebsite(
            title="Suối Tiên",
            diachi="TP.HCM",
            tencty="Công ty Suối Tiên",
            slogan="Điểm đến số 1",
            message="Chào mừng",
            description="Mô tả website",
            theme="default",
        )
        web.save()
        self.assertEqual(web.title, "[[[:vi]]]Suối Tiên[[[:end_vi]]]")
        self.assertEqual(web.diachi, "[[[:vi]]]TP.HCM[[[:end_vi]]]")
        self.assertEqual(web.tencty, "[[[:vi]]]Công ty Suối Tiên[[[:end_vi]]]")
        self.assertEqual(web.slogan, "[[[:vi]]]Điểm đến số 1[[[:end_vi]]]")
        self.assertEqual(web.message, "[[[:vi]]]Chào mừng[[[:end_vi]]]")
        self.assertEqual(web.description, "[[[:vi]]]Mô tả website[[[:end_vi]]]")

    # ================================================================
    # 14-15. HalinkAdmin + HalinkUser: Hash password md5(md5())
    # PHP user/add.php:20 → md5(md5($_POST['txtpass']))
    # PHP thanhvien/add.php:14 → md5(md5($_POST['password']))
    # ================================================================

    def test_admin_password_hashing(self):
        """Admin CMS: password phải hash md5(md5()) giống PHP user/add.php."""
        admin_user = HalinkAdmin(
            username="testadmin",
            password="mypassword123",
            email="admin@test.com",
            level=1,
        )
        admin_user.save()

        # Tính hash kỳ vọng
        expected = _md5_double_hash("mypassword123")
        self.assertEqual(admin_user.password, expected)
        self.assertTrue(_is_md5_hash(admin_user.password))

        # Lưu lại lần 2 không được hash trùng (đã là md5 rồi → giữ nguyên)
        saved_hash = admin_user.password
        admin_user.save()
        self.assertEqual(admin_user.password, saved_hash)

    def test_user_password_hashing(self):
        """Thành viên: password phải hash md5(md5()) giống PHP thanhvien/add.php."""
        user = HalinkUser(
            username="testmember",
            password="memberpass456",
            email="member@test.com",
        )
        user.save()

        expected = _md5_double_hash("memberpass456")
        self.assertEqual(user.password, expected)
        self.assertTrue(_is_md5_hash(user.password))

        # Lưu lại lần 2 không hash trùng
        saved_hash = user.password
        user.save()
        self.assertEqual(user.password, saved_hash)

    # ================================================================
    # 16. Helper functions: _is_md5_hash và _md5_double_hash
    # ================================================================

    def test_md5_helper_functions(self):
        """Kiểm tra các hàm tiện ích hash MD5."""
        # _md5_double_hash cho kết quả đúng
        # md5("test") = 098f6bcd4621d373cade4e832627b4f6
        # md5("098f6bcd4621d373cade4e832627b4f6") = fb469d7ef430b0baf0cab6c436e70375
        result = _md5_double_hash("test")
        self.assertEqual(result, "fb469d7ef430b0baf0cab6c436e70375")

        # _is_md5_hash kiểm tra đúng
        self.assertTrue(_is_md5_hash("fb469d7ef430b0baf0cab6c436e70375"))
        self.assertFalse(_is_md5_hash("plaintext"))
        self.assertFalse(_is_md5_hash(""))
        self.assertFalse(_is_md5_hash(None))
