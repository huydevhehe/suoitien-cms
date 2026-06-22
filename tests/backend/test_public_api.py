import json

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from suoi_tien.models import HalinkWebsite, HalinkMenu, HalinkFlash, HalinkPost
from suoi_tien.models.proxies import CommentProxy, TicketOrderProxy

PRODUCT_PRICE_ADULT = 150000
PRODUCT_PRICE_CHILD = 100000


class PublicAPITestCase(APITestCase):
    """Test 11 API Public (/api/public/) — chỉ đọc + tạo mới, không cần đăng nhập."""

    def setUp(self):
        cache.clear()

        self.website = HalinkWebsite.objects.create(
            id=1, title='Suối Tiên', slogan='Vui hết mình',
            hotline='1900 1009', active_chonve='1', theme='{}',
            st_accesstoken='secret-token-khong-duoc-lo',
        )
        self.menu = HalinkMenu.objects.create(
            id_cat=1, title_cat='Trang chủ',
            content_menu='https://suoitien.com***_link_***0',
            ticlock=0,
        )
        self.banner = HalinkFlash.objects.create(
            file_vn='banner.jpg', link='/', ticlock=0,
        )

        self.product_adult = HalinkPost.objects.create(
            title_vn='Vé người lớn', alias='ve-nguoi-lon',
            description_vn='Vé vào cổng người lớn',
            post_type='product', ticlock='0', post_amount=PRODUCT_PRICE_ADULT,
        )
        self.product_child = HalinkPost.objects.create(
            title_vn='Vé trẻ em', alias='ve-tre-em',
            post_type='product', ticlock='0', post_amount=PRODUCT_PRICE_CHILD,
        )
        self.product_hidden = HalinkPost.objects.create(
            title_vn='Vé ẩn (ngừng bán)', alias='ve-an',
            post_type='product', ticlock='1', post_amount=999999,
        )

        self.approved_comment = CommentProxy.objects.create(
            Id_post=self.product_adult.Id, meta_type='comment_post',
            meta_value=json.dumps([
                {'name': 'comment_name', 'value': 'Khách A'},
                {'name': 'comment_content', 'value': 'Rất vui!'},
                {'name': 'comment_star', 'value': '5'},
            ], ensure_ascii=False),
            ticlock=0, date=timezone.now(),
        )
        self.pending_comment = CommentProxy.objects.create(
            Id_post=self.product_adult.Id, meta_type='comment_post',
            meta_value=json.dumps([
                {'name': 'comment_name', 'value': 'Khách B (chờ duyệt)'},
                {'name': 'comment_content', 'value': 'Spam?'},
                {'name': 'comment_star', 'value': '1'},
            ], ensure_ascii=False),
            ticlock=1, date=timezone.now(),
        )

    def tearDown(self):
        cache.clear()

    # ---------- GET /settings/ ----------

    def test_settings_returns_public_fields_only(self):
        response = self.client.get(reverse('public-settings'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['hotline'], '1900 1009')
        self.assertNotIn('st_accesstoken', response.data)
        self.assertNotIn('theme', response.data)

    # ---------- GET /menus/ ----------

    def test_menus_returns_tree_and_hides_locked(self):
        HalinkMenu.objects.create(id_cat=2, title_cat='Menu ẩn', content_menu='', ticlock=1)
        response = self.client.get(reverse('public-menus'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Trang chủ')
        self.assertEqual(len(response.data[0]['items']), 1)

    # ---------- GET /banners/ ----------

    def test_banners_hides_locked(self):
        HalinkFlash.objects.create(file_vn='banner-an.jpg', link='/', ticlock=1)
        response = self.client.get(reverse('public-banners'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # ---------- GET /posts/ ----------

    def test_posts_list_filters_by_post_type_and_hides_locked(self):
        response = self.client.get(reverse('public-post-list'), {'post_type': 'product'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item['Id'] for item in response.data}
        self.assertIn(self.product_adult.Id, returned_ids)
        self.assertIn(self.product_child.Id, returned_ids)
        self.assertNotIn(self.product_hidden.Id, returned_ids)

    def test_posts_list_search_by_title(self):
        response = self.client.get(reverse('public-post-list'), {'search': 'trẻ em'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item['Id'] for item in response.data}
        self.assertEqual(returned_ids, {self.product_child.Id})

    def test_posts_list_ordering(self):
        response = self.client.get(reverse('public-post-list'), {
            'post_type': 'product', 'ordering': '-post_views',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ---------- GET /posts/{alias}/ ----------

    def test_post_detail_increments_post_views(self):
        url = reverse('public-post-detail', kwargs={'alias': self.product_adult.alias})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['post_views'], 1)
        self.product_adult.refresh_from_db()
        self.assertEqual(self.product_adult.post_views, 1)

    def test_post_detail_404_when_hidden_or_missing(self):
        hidden_url = reverse('public-post-detail', kwargs={'alias': self.product_hidden.alias})
        self.assertEqual(self.client.get(hidden_url).status_code, status.HTTP_404_NOT_FOUND)

        missing_url = reverse('public-post-detail', kwargs={'alias': 'khong-ton-tai'})
        self.assertEqual(self.client.get(missing_url).status_code, status.HTTP_404_NOT_FOUND)

    # ---------- GET/POST /comments/ ----------

    def test_comments_list_only_approved(self):
        response = self.client.get(reverse('public-comments'), {'id_post': self.product_adult.Id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item['Id'] for item in response.data}
        self.assertEqual(returned_ids, {self.approved_comment.Id})

    def test_comment_create_success_goes_to_pending(self):
        response = self.client.post(reverse('public-comments'), {
            'id_post': self.product_adult.Id, 'fullname': 'Khách mới',
            'content': 'Rất hài lòng', 'star': 5,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = CommentProxy.objects.filter(meta_type='comment_post').exclude(
            Id__in=[self.approved_comment.Id, self.pending_comment.Id],
        ).first()
        self.assertIsNotNone(created)
        self.assertEqual(created.ticlock, 1)

    def test_comment_create_rejects_unknown_post(self):
        response = self.client.post(reverse('public-comments'), {
            'id_post': 999999, 'fullname': 'Khách', 'content': 'abc', 'star': 5,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_create_rejects_star_out_of_range(self):
        response = self.client.post(reverse('public-comments'), {
            'id_post': self.product_adult.Id, 'fullname': 'Khách',
            'content': 'abc', 'star': 6,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_create_rejects_missing_content(self):
        response = self.client.post(reverse('public-comments'), {
            'id_post': self.product_adult.Id, 'fullname': 'Khách', 'star': 5,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------- POST /ticket-orders/ ----------

    def _ticket_order_payload(self, **overrides):
        payload = {
            'fullname': 'Nguyễn Văn A', 'phone': '0901234567',
            'email': 'a@example.com', 'address': 'TPHCM',
            'dateoforg': '2026-07-01', 'type_payment': 1,
            'items': [
                {'post_id': self.product_adult.Id, 'quantity': 2},
                {'post_id': self.product_child.Id, 'quantity': 1},
            ],
        }
        payload.update(overrides)
        return payload

    def test_ticket_order_create_recomputes_price_from_db_not_client(self):
        response = self.client.post(
            reverse('public-ticket-order-create'), self._ticket_order_payload(),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id_cart', response.data)

        order = TicketOrderProxy.objects.get(id_cart=response.data['id_cart'])
        expected_total = 2 * PRODUCT_PRICE_ADULT + 1 * PRODUCT_PRICE_CHILD
        self.assertEqual(order.computed_total_price_num, expected_total)
        # Input không có chỗ để gửi giá — chỉ post_id + quantity, server tự tra post_amount.
        for item in self._ticket_order_payload()['items']:
            self.assertEqual(set(item.keys()), {'post_id', 'quantity'})

    def test_ticket_order_rejects_unknown_or_hidden_product(self):
        response = self.client.post(
            reverse('public-ticket-order-create'),
            self._ticket_order_payload(items=[{'post_id': self.product_hidden.Id, 'quantity': 1}]),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ticket_order_rejects_empty_items(self):
        response = self.client.post(
            reverse('public-ticket-order-create'),
            self._ticket_order_payload(items=[]),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------- GET /ticket-orders/lookup/ ----------

    def test_ticket_order_lookup_requires_matching_id_and_phone(self):
        create_response = self.client.post(
            reverse('public-ticket-order-create'), self._ticket_order_payload(),
            format='json',
        )
        id_cart = create_response.data['id_cart']

        ok_response = self.client.get(reverse('public-ticket-order-lookup'), {
            'id_cart': id_cart, 'phone': '0901234567',
        })
        self.assertEqual(ok_response.status_code, status.HTTP_200_OK)
        self.assertEqual(ok_response.data['id_cart'], id_cart)

        wrong_phone_response = self.client.get(reverse('public-ticket-order-lookup'), {
            'id_cart': id_cart, 'phone': '0999999999',
        })
        self.assertEqual(wrong_phone_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ticket_order_lookup_requires_both_params(self):
        response = self.client.get(reverse('public-ticket-order-lookup'), {'id_cart': 'DH123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------- POST /food-orders/ ----------

    def test_food_order_create_success(self):
        response = self.client.post(reverse('public-food-order-create'), {
            'fullname': 'Trần B', 'phone': '0911111111', 'address': 'TPHCM',
            'items': [{'post_id': self.product_adult.Id, 'quantity': 3}],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_price'], str(3 * PRODUCT_PRICE_ADULT))

    def test_food_order_rejects_unknown_product(self):
        response = self.client.post(reverse('public-food-order-create'), {
            'fullname': 'Trần B', 'phone': '0911111111',
            'items': [{'post_id': 999999, 'quantity': 1}],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------- POST /supports/ ----------

    def test_support_create_success(self):
        response = self.client.post(reverse('public-support-create'), {
            'subject': 'Hỏi về combo vé', 'message': 'Cho hỏi giá combo hè?',
            'fullname': 'Lê C', 'phone': '0922222222', 'email': 'c@example.com',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_support_create_rejects_missing_required_fields(self):
        response = self.client.post(reverse('public-support-create'), {'fullname': 'Lê C'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------- Throttle public_write (20/phút/IP) ----------

    def test_write_throttle_blocks_after_limit(self):
        last_response = None
        for _ in range(21):
            last_response = self.client.post(reverse('public-support-create'), {
                'subject': 'Spam test', 'message': 'spam spam spam',
            })
        self.assertEqual(last_response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
