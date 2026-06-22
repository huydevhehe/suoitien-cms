"""
Test sâu các nghiệp vụ Admin còn lại (ngoài phạm vi test_admin_smoke.py):
gửi email, giá sản phẩm, đổi mật khẩu, upload ảnh, Sidebar/JSON widget,
Dashboard, và độ chính xác của bộ lọc changelist.

Mọi test chạy trên DB test riêng (Django tự tạo/xóa). Test gửi email KHÔNG
gửi email thật — Django test runner tự chuyển EMAIL_BACKEND sang locmem,
email được lưu vào `django.core.mail.outbox` để kiểm tra.
"""
import json
import os
import time

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from suoi_tien.models import HalinkAdmin, HalinkUser, HalinkPost, HalinkCart, HalinkMeta
from suoi_tien.models.proxies import TicketOrderProxy, FoodOrderProxy, ProductProxy
from suoi_tien.models.helpers import _md5_double_hash


class EmailResendActionTestCase(TestCase):
    """Action 'resend_confirmation_email' của TicketOrderProxyAdmin/FoodOrderProxyAdmin."""

    def setUp(self):
        self.superuser = User.objects.create_superuser('smoke_admin2', 'a@a.com', 'pass12345')
        self.client.force_login(self.superuser)
        mail.outbox = []

    def test_resend_ticket_order_email_sends_to_valid_email(self):
        order = TicketOrderProxy.objects.create(
            id_cart='DH_EMAIL_TEST', info_product='1***+++***1***+++***100000',
            info_user='null***+++***Khách Test***+++***0900000000***+++***khach@example.com***+++***Địa chỉ***+++***',
            type_payment=1, date=timezone.now(), status=0, ticlock=1,
        )
        response = self.client.post(reverse('admin:suoi_tien_ticketorderproxy_changelist'), {
            'action': 'resend_confirmation_email',
            '_selected_action': [str(order.pk)],
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['khach@example.com'])
        # Email gửi dạng HTML (EmailMultiAlternatives) — body chỉ là text fallback,
        # nội dung thật nằm trong alternatives[0].
        html_body = mail.outbox[0].alternatives[0][0]
        self.assertIn(order.id_cart, html_body)

    def test_resend_ticket_order_email_skips_invalid_email(self):
        order = TicketOrderProxy.objects.create(
            id_cart='DH_EMAIL_TEST_2', info_product='1***+++***1***+++***100000',
            info_user='null***+++***Khách Test***+++***0900000000***+++***khong-co-email***+++***Địa chỉ***+++***',
            type_payment=1, date=timezone.now(), status=0, ticlock=1,
        )
        self.client.post(reverse('admin:suoi_tien_ticketorderproxy_changelist'), {
            'action': 'resend_confirmation_email',
            '_selected_action': [str(order.pk)],
        }, follow=True)
        self.assertEqual(len(mail.outbox), 0)

    def test_resend_food_order_email_sends_to_valid_email(self):
        order = FoodOrderProxy.objects.create(
            meta_type='order-food', meta_title='dat_mon_online',
            meta_value=json.dumps([{'id': 1, 'qtv': 1, 'price': 50000}]),
            meta_value_cus=json.dumps([
                {'name': 'fullname', 'value': 'Khách Test'},
                {'name': 'email', 'value': 'khach-mon@example.com'},
            ]),
            date=timezone.now(),
        )
        self.client.post(reverse('admin:suoi_tien_foodorderproxy_changelist'), {
            'action': 'resend_confirmation_email',
            '_selected_action': [str(order.pk)],
        }, follow=True)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['khach-mon@example.com'])


class ProductPriceFormTestCase(TestCase):
    """ProductAdminForm: giá bán/giá khuyến mãi lưu qua bảng HalinkMeta riêng."""

    def setUp(self):
        self.superuser = User.objects.create_superuser('smoke_admin3', 'a@a.com', 'pass12345')
        self.client.force_login(self.superuser)
        self.product = HalinkPost.objects.create(
            title_vn='Sản phẩm test giá', alias='san-pham-test-gia',
            post_type='product', ticlock='0', sort=1, date=int(time.time()),
        )

    def _payload(self, price, promo_price, ticlock_checked=True):
        data = {
            'title_vn_0': 'Sản phẩm test giá', 'title_vn_1': '',
            'alias': 'san-pham-test-gia',
            'description_vn_0': '', 'description_vn_1': '',
            'content_vn_0': '', 'content_vn_1': '',
            'price': str(price), 'promo_price': str(promo_price),
            'post_image': '', 'post_gallery': '',
            'sort': '1',
            '_save': 'Lưu',
        }
        if ticlock_checked:
            data['ticlock'] = 'on'
        return data

    def test_save_creates_price_metadata(self):
        url = reverse('admin:suoi_tien_productproxy_change', args=[self.product.pk])
        response = self.client.post(url, self._payload(150000, 120000), follow=True)
        self.assertEqual(response.status_code, 200)

        price_meta = HalinkMeta.objects.get(Id_post=self.product.pk, meta_title='halink_metabox_gia')
        promo_meta = HalinkMeta.objects.get(Id_post=self.product.pk, meta_title='halink_metabox_gia_khuyen_mai')
        self.assertEqual(price_meta.meta_value, '150000')
        self.assertEqual(promo_meta.meta_value, '120000')

    def test_save_again_updates_existing_price_metadata(self):
        url = reverse('admin:suoi_tien_productproxy_change', args=[self.product.pk])
        self.client.post(url, self._payload(150000, 120000), follow=True)
        self.client.post(url, self._payload(200000, 180000), follow=True)

        self.assertEqual(
            HalinkMeta.objects.filter(Id_post=self.product.pk, meta_title='halink_metabox_gia').count(), 1,
        )
        price_meta = HalinkMeta.objects.get(Id_post=self.product.pk, meta_title='halink_metabox_gia')
        self.assertEqual(price_meta.meta_value, '200000')


class PasswordChangeFormTestCase(TestCase):
    """Form đổi mật khẩu Admin/Thành viên: hash kiểu PHP cũ md5(md5(password))."""

    def setUp(self):
        self.superuser = User.objects.create_superuser('smoke_admin4', 'a@a.com', 'pass12345')
        self.client.force_login(self.superuser)

    def test_halink_admin_new_password_gets_double_md5_hashed(self):
        # Model tự hash khi tạo mới (xem HalinkAdmin.save()) — truyền plain text,
        # không tự hash trước, nếu không sẽ bị hash chồng 2 lần.
        target = HalinkAdmin.objects.create(
            username='cms_admin_test', password='old_password',
            email='cms@example.com', level=1, fullname='CMS Admin Test',
        )
        url = reverse('admin:suoi_tien_halinkadmin_change', args=[target.pk])
        response = self.client.post(url, {
            'username': 'cms_admin_test', 'email': 'cms@example.com',
            'level': '1', 'fullname': 'CMS Admin Test',
            'new_password': 'new_secret_123',
            '_save': 'Lưu',
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        target.refresh_from_db()
        self.assertEqual(target.password, _md5_double_hash('new_secret_123'))

    def test_halink_admin_blank_new_password_keeps_old_hash(self):
        target = HalinkAdmin.objects.create(
            username='cms_admin_test2', password='keep_me',
            email='cms2@example.com', level=1, fullname='CMS Admin Test 2',
        )
        old_hash = target.password  # giá trị thật sau khi model tự hash lúc tạo
        url = reverse('admin:suoi_tien_halinkadmin_change', args=[target.pk])
        self.client.post(url, {
            'username': 'cms_admin_test2', 'email': 'cms2@example.com',
            'level': '1', 'fullname': 'CMS Admin Test 2',
            'new_password': '',
            '_save': 'Lưu',
        }, follow=True)

        target.refresh_from_db()
        self.assertEqual(target.password, old_hash)

    def test_halink_user_new_password_gets_double_md5_hashed(self):
        target = HalinkUser.objects.create(
            username='member_test', password='old_password',
            email='member@example.com', fullname='Member Test', ticlock=0,
        )
        url = reverse('admin:suoi_tien_halinkuser_change', args=[target.pk])
        response = self.client.post(url, {
            'username': 'member_test', 'email': 'member@example.com',
            'fullname': 'Member Test', 'ticlock': 'on',
            'new_password': 'member_new_pw',
            '_save': 'Lưu',
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        target.refresh_from_db()
        self.assertEqual(target.password, _md5_double_hash('member_new_pw'))


class ImageUploadTestCase(TestCase):
    """Upload ảnh mới qua popup Image Picker (suoi_tien/views.py: image_browser_view)."""

    def setUp(self):
        self.superuser = User.objects.create_superuser('smoke_admin5', 'a@a.com', 'pass12345')
        self.client.force_login(self.superuser)
        self.uploaded_paths = []

    def tearDown(self):
        for rel_path in self.uploaded_paths:
            full_path = os.path.join(settings.MEDIA_ROOT, rel_path)
            if os.path.exists(full_path):
                os.remove(full_path)

    def _fake_image_file(self, name='test_upload_image.png'):
        from django.core.files.uploadedfile import SimpleUploadedFile
        png_1x1 = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
            b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        return SimpleUploadedFile(name, png_1x1, content_type='image/png')

    def test_upload_saves_file_to_subfolder(self):
        url = reverse('admin_image_browser')
        response = self.client.post(url, {
            'upload_file': self._fake_image_file('test_upload_image.png'),
            'field_id': 'id_post_image', 'subfolder': 'hinhanh',
        })
        self.assertEqual(response.status_code, 302)  # redirect về GET sau khi upload xong

        expected_path = os.path.join(settings.MEDIA_ROOT, 'hinhanh', 'test_upload_image.png')
        self.assertTrue(os.path.exists(expected_path))
        self.uploaded_paths.append('hinhanh/test_upload_image.png')

    def test_upload_same_filename_twice_does_not_overwrite(self):
        url = reverse('admin_image_browser')
        self.client.post(url, {
            'upload_file': self._fake_image_file('duplicate_test.png'),
            'field_id': 'id_post_image', 'subfolder': 'hinhanh',
        })
        self.client.post(url, {
            'upload_file': self._fake_image_file('duplicate_test.png'),
            'field_id': 'id_post_image', 'subfolder': 'hinhanh',
        })

        self.uploaded_paths += ['hinhanh/duplicate_test.png', 'hinhanh/duplicate_test_1.png']
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, 'hinhanh', 'duplicate_test.png')))
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, 'hinhanh', 'duplicate_test_1.png')))

    def test_upload_rejects_disallowed_extension(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        url = reverse('admin_image_browser')
        response = self.client.post(url, {
            'upload_file': SimpleUploadedFile('malicious.exe', b'MZ...', content_type='application/octet-stream'),
            'field_id': 'id_post_image', 'subfolder': 'hinhanh',
        })
        # Không redirect (không có nhánh xử lý upload thành công) -> trả thẳng trang danh sách ảnh.
        self.assertEqual(response.status_code, 200)
        full_path = os.path.join(settings.MEDIA_ROOT, 'hinhanh', 'malicious.exe')
        self.assertFalse(os.path.exists(full_path))


class SidebarCheckboxWidgetTestCase(TestCase):
    """SidebarCheckboxWidget (suoi_tien/widgets.py) — chọn sidebar dạng checkbox."""

    def test_value_from_datadict_returns_json_list(self):
        from django.http import QueryDict
        from suoi_tien.widgets import SidebarCheckboxWidget
        widget = SidebarCheckboxWidget()
        data = QueryDict(mutable=True)
        data.setlist('post_sidebar', ['halink_header_wg', 'halink_footer0_wg'])
        result = widget.value_from_datadict(data, {}, 'post_sidebar')
        self.assertEqual(json.loads(result), ['halink_header_wg', 'halink_footer0_wg'])

    def test_value_from_datadict_empty_when_nothing_checked(self):
        from django.http import QueryDict
        from suoi_tien.widgets import SidebarCheckboxWidget
        widget = SidebarCheckboxWidget()
        result = widget.value_from_datadict(QueryDict(mutable=True), {}, 'post_sidebar')
        self.assertEqual(result, '')

    def test_render_marks_selected_sidebar_as_checked(self):
        from suoi_tien.widgets import SidebarCheckboxWidget
        widget = SidebarCheckboxWidget()
        html = widget.render('post_sidebar', json.dumps(['halink_header_wg']))
        self.assertIn('value="halink_header_wg" checked', html)
        self.assertNotIn('value="halink_footer0_wg" checked', html)


class JSONTextAreaWidgetTestCase(TestCase):
    """JSONTextAreaWidget (suoi_tien/widgets.py) — tự định dạng đẹp JSON."""

    def test_format_value_pretty_prints_valid_json(self):
        from suoi_tien.widgets import JSONTextAreaWidget
        widget = JSONTextAreaWidget()
        result = widget.format_value('{"a":1,"b":[1,2,3]}')
        self.assertEqual(json.loads(result), {'a': 1, 'b': [1, 2, 3]})
        self.assertIn('\n', result)  # đã có indent xuống dòng

    def test_format_value_returns_raw_text_when_invalid_json(self):
        from suoi_tien.widgets import JSONTextAreaWidget
        widget = JSONTextAreaWidget()
        result = widget.format_value('khong phai json')
        self.assertEqual(result, 'khong phai json')


class DashboardTestCase(TestCase):
    """Trang chủ Admin (Unfold dashboard_callback) — suoi_tien/dashboard.py."""

    def setUp(self):
        self.superuser = User.objects.create_superuser('smoke_admin6', 'a@a.com', 'pass12345')
        self.client.force_login(self.superuser)

    def test_admin_index_loads_with_stats(self):
        HalinkUser.objects.create(username='u1', fullname='User 1', ticlock=0)
        HalinkPost.objects.create(title_vn='Bài viết', post_type='post', ticlock='0', date=int(time.time()))
        HalinkCart.objects.create(
            id_cart='DH_DASH_TEST', info_product='1***+++***1***+++***50000',
            info_user='null***+++***A***+++***0900000000', type_payment=1,
            date=timezone.now(), status=4, ticlock=1,
        )

        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('stats', response.context)
        self.assertEqual(response.context['stats']['total_users'], 1)
        self.assertEqual(response.context['stats']['total_posts'], 1)
        self.assertEqual(response.context['stats']['total_ticket_orders'], 1)

    def test_admin_index_loads_with_no_data(self):
        # Trang chủ phải không lỗi 500 ngay cả khi DB hoàn toàn trống.
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)


class ChangelistFilterTestCase(TestCase):
    """Độ chính xác của list_filter trên changelist (không chỉ load được trang)."""

    def setUp(self):
        self.superuser = User.objects.create_superuser('smoke_admin7', 'a@a.com', 'pass12345')
        self.client.force_login(self.superuser)
        now_ts = int(time.time())
        self.visible_post = HalinkPost.objects.create(
            title_vn='Bài hiện', alias='bai-hien', post_type='post', ticlock='0', date=now_ts,
        )
        self.hidden_post = HalinkPost.objects.create(
            title_vn='Bài ẩn', alias='bai-an', post_type='post', ticlock='1', date=now_ts,
        )

    def test_filter_by_ticlock_returns_only_matching_rows(self):
        url = reverse('admin:suoi_tien_postproxy_changelist')
        response = self.client.get(url, {'ticlock': '1'})
        self.assertEqual(response.status_code, 200)

        result_list = response.context['cl'].result_list
        result_ids = {obj.pk for obj in result_list}
        self.assertIn(self.hidden_post.pk, result_ids)
        self.assertNotIn(self.visible_post.pk, result_ids)

    def test_search_by_title_returns_only_matching_rows(self):
        url = reverse('admin:suoi_tien_postproxy_changelist')
        response = self.client.get(url, {'q': 'Bài ẩn'})
        result_ids = {obj.pk for obj in response.context['cl'].result_list}
        self.assertEqual(result_ids, {self.hidden_post.pk})
