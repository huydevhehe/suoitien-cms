import json
import time

from django.contrib import admin as django_admin
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone

from suoi_tien.models import (
    HalinkAdmin, HalinkUser, HalinkPost, HalinkFlash, HalinkMenu,
    HalinkMeta, HalinkMetabox, HalinkStatistic, HalinkWebsite,
)
from suoi_tien.models.proxies import (
    PostProxy, PostCategoryProxy, PageProxy, ProductProxy, ProductCategoryProxy,
    TicketOrderProxy, FoodOrderProxy, CommentProxy, SupportProxy,
    LanguageProxy, SMTPProxy,
)


class AdminSmokeTestCase(TestCase):
    """
    Lưới an toàn cho toàn bộ Django Admin: quét hết các trang đã đăng ký,
    đảm bảo không trang nào lỗi 500 trước khi refactor chia nhỏ file admin/models.
    """

    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username='smoke_admin', email='smoke@example.com', password='smoke12345',
        )

        now_ts = int(time.time())

        cls.post = HalinkPost.objects.create(
            title_vn='Bài viết test', alias='bai-viet-test', post_type='post',
            ticlock='0', sort=1, home=0, date=now_ts,
        )
        cls.postcat = HalinkPost.objects.create(
            title_vn='Chuyên mục bài viết test', alias='chuyen-muc-bai-viet-test',
            post_type='postcat', ticlock='0', sort=1, date=now_ts,
        )
        cls.page = HalinkPost.objects.create(
            title_vn='Trang tĩnh test', alias='trang-tinh-test', post_type='page',
            ticlock='0', date=now_ts,
        )
        cls.product = HalinkPost.objects.create(
            title_vn='Sản phẩm test', alias='san-pham-test', post_type='product',
            ticlock='0', sort=1, post_amount=100000, date=now_ts,
        )
        cls.productcat = HalinkPost.objects.create(
            title_vn='Chuyên mục sản phẩm test', alias='chuyen-muc-san-pham-test',
            post_type='productcat', ticlock='0', sort=1, date=now_ts,
        )

        cls.flash = HalinkFlash.objects.create(
            file_vn='banner-test.jpg', title_vn='Banner test', link='/', ticlock=0, date=now_ts,
        )
        cls.menu = HalinkMenu.objects.create(
            id_cat=1, title_cat='Menu test', content_menu='', ticlock=0,
        )
        cls.website = HalinkWebsite.objects.create(
            id=1, title='Website test', active_chonve='1', theme='{}',
        )
        cls.statistic = HalinkStatistic.objects.create(
            ip='127.0.0.1', id_post='1', url='/test', date=timezone.now(),
        )
        cls.metabox = HalinkMetabox.objects.create(
            meta_title='Metabox test', meta_key='gia', meta_type='product_meta',
            post_type='product', ticlock=0,
        )

        cls.ticket_order = TicketOrderProxy.objects.create(
            id_cart='DH_SMOKE_TEST', info_product='1***+++***1***+++***100000',
            info_user='null***+++***Khách test***+++***0900000000***+++***a@b.com***+++***Địa chỉ test***+++***',
            type_payment=1, date=timezone.now(), status=0, ticlock=1,
        )
        cls.food_order = FoodOrderProxy.objects.create(
            meta_type='order-food', meta_title='dat_mon_online',
            meta_value=json.dumps([{'id': cls.product.Id, 'qtv': 1, 'price': 100000}], ensure_ascii=False),
            meta_value_cus=json.dumps([
                {'name': 'fullname', 'value': 'Khách test'},
                {'name': 'phone', 'value': '0900000000'},
                {'name': 'address', 'value': 'Địa chỉ test'},
            ], ensure_ascii=False),
            date=timezone.now(),
        )
        cls.comment = CommentProxy.objects.create(
            Id_post=cls.product.Id, meta_type='comment_post',
            meta_value=json.dumps([
                {'name': 'comment_name', 'value': 'Khách test'},
                {'name': 'comment_content', 'value': 'Bình luận test'},
                {'name': 'comment_star', 'value': '5'},
            ], ensure_ascii=False),
            ticlock=0, date=timezone.now(),
        )
        cls.support = SupportProxy.objects.create(
            meta_type='support', meta_title='Chủ đề test', meta_value='Nội dung hỗ trợ test',
            date=timezone.now(),
        )
        cls.language = LanguageProxy.objects.create(
            meta_type='halinklanguage', meta_title='key_test', meta_value='Giá trị test',
            date=timezone.now(),
        )
        cls.smtp = SMTPProxy.objects.create(
            meta_type='halinksmtp', meta_title='smtp_host', meta_value='smtp.test.com',
            date=timezone.now(),
        )
        cls.halink_admin = HalinkAdmin.objects.create(
            username='admin_smoke', password='x', email='admin_smoke@example.com',
            level=1, fullname='Admin Smoke',
        )
        cls.halink_user = HalinkUser.objects.create(
            username='user_smoke', password='x', email='user_smoke@example.com',
            fullname='User Smoke', ticlock=0,
        )

        cls.fixture_by_model = {
            HalinkFlash: cls.flash,
            HalinkMenu: cls.menu,
            HalinkWebsite: cls.website,
            HalinkStatistic: cls.statistic,
            HalinkMetabox: cls.metabox,
            HalinkMeta: cls.support._meta.model.objects.get(pk=cls.support.pk),
            PostProxy: cls.post,
            PostCategoryProxy: cls.postcat,
            PageProxy: cls.page,
            ProductProxy: cls.product,
            ProductCategoryProxy: cls.productcat,
            TicketOrderProxy: cls.ticket_order,
            FoodOrderProxy: cls.food_order,
            CommentProxy: cls.comment,
            SupportProxy: cls.support,
            LanguageProxy: cls.language,
            SMTPProxy: cls.smtp,
            HalinkAdmin: cls.halink_admin,
            HalinkUser: cls.halink_user,
        }

    def setUp(self):
        self.client.force_login(self.superuser)
        self.request_factory = RequestFactory()

    def _build_fake_request(self):
        request = self.request_factory.get('/admin/')
        request.user = self.superuser
        return request

    def test_all_changelist_pages_return_200(self):
        for model, model_admin in django_admin.site._registry.items():
            opts = model._meta
            url = reverse(f'admin:{opts.app_label}_{opts.model_name}_changelist')
            response = self.client.get(url)
            self.assertEqual(
                response.status_code, 200,
                f"Trang danh sách của {model.__name__} ({url}) trả về {response.status_code}",
            )

    def test_all_change_pages_return_200(self):
        for model, model_admin in django_admin.site._registry.items():
            instance = self.fixture_by_model.get(model)
            if instance is None:
                continue
            opts = model._meta
            url = reverse(f'admin:{opts.app_label}_{opts.model_name}_change', args=[instance.pk])
            response = self.client.get(url)
            self.assertEqual(
                response.status_code, 200,
                f"Trang chi tiết của {model.__name__} ({url}) trả về {response.status_code}",
            )

    def test_all_add_pages_return_200(self):
        request = self._build_fake_request()
        for model, model_admin in django_admin.site._registry.items():
            if not model_admin.has_add_permission(request):
                continue
            opts = model._meta
            url = reverse(f'admin:{opts.app_label}_{opts.model_name}_add')
            response = self.client.get(url)
            self.assertEqual(
                response.status_code, 200,
                f"Trang thêm mới của {model.__name__} ({url}) trả về {response.status_code}",
            )

    def test_django_check_no_errors(self):
        call_command('check')


class StatusSwitchWidgetTestCase(TestCase):
    """
    Test trực tiếp StatusSwitchWidget (suoi_tien/widgets.py) — vùng rủi ro cao nhất,
    đã từng có 2 bug thật ("Fix status switch reversed logic for ticlock",
    "Fix StatusSwitchWidget check_test bug causing 0/1 to not save"). Test ở mức
    widget (không qua toàn bộ form Admin) để chắc chắn không bị ảnh hưởng bởi các
    field khác khi refactor.
    """

    def test_reversed_field_checked_means_value_0(self):
        from suoi_tien.widgets import StatusSwitchWidget
        widget = StatusSwitchWidget(is_char=True, reversed=True)
        self.assertEqual(widget.value_from_datadict({'ticlock': 'on'}, {}, 'ticlock'), '0')
        self.assertEqual(widget.value_from_datadict({}, {}, 'ticlock'), '1')

    def test_reversed_field_check_test_matches_db_value(self):
        from suoi_tien.widgets import StatusSwitchWidget
        widget = StatusSwitchWidget(is_char=True, reversed=True)
        self.assertTrue(widget.check_test('0'))
        self.assertFalse(widget.check_test('1'))

    def test_normal_field_checked_means_value_1(self):
        from suoi_tien.widgets import StatusSwitchWidget
        widget = StatusSwitchWidget(is_char=False, reversed=False)
        self.assertEqual(widget.value_from_datadict({'home': 'on'}, {}, 'home'), 1)
        self.assertEqual(widget.value_from_datadict({}, {}, 'home'), 0)

    def test_normal_field_check_test_matches_db_value(self):
        from suoi_tien.widgets import StatusSwitchWidget
        widget = StatusSwitchWidget(is_char=False, reversed=False)
        self.assertTrue(widget.check_test(1))
        self.assertFalse(widget.check_test(0))
