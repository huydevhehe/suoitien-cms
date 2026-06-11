from django.core.management.base import BaseCommand
from suoi_tien.models import HalinkPost, HalinkCart, HalinkMeta
import re
import json

class Command(BaseCommand):
    help = 'Quét đối chiếu định dạng dữ liệu giữa Django và PHP CMS cũ (Data Parity)'

    def handle(self, *args, **options):
        import sys
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
            
        self.stdout.write(self.style.SUCCESS("=== BẮT ĐẦU QUÉT ĐỐI CHIẾU DỮ LIỆU (DATA PARITY AUDIT) ==="))
        
        # 1. Quét bài viết/sản phẩm (HalinkPost)
        self.stdout.write("--- 1. Kiểm tra Định dạng Đa ngôn ngữ (HalinkPost) ---")
        posts = HalinkPost.objects.all()
        invalid_posts_count = 0
        
        for post in posts:
            issues = []
            # Kiểm tra tiêu đề
            if post.title_vn and '[[[:' not in post.title_vn:
                issues.append("title_vn không có tag ngôn ngữ")
            # Kiểm tra mô tả
            if post.description_vn and '[[[:' not in post.description_vn:
                issues.append("description_vn không có tag ngôn ngữ")
            # Kiểm tra nội dung
            if post.content_vn and '[[[:' not in post.content_vn:
                issues.append("content_vn không có tag ngôn ngữ")
                
            if issues:
                invalid_posts_count += 1
                self.stdout.write(self.style.WARNING(
                    f"Post #{post.Id} (Loại: {post.post_type}): {', '.join(issues)} | Dữ liệu thô: {post.title_vn[:50] if post.title_vn else ''}..."
                ))
        
        self.stdout.write(self.style.SUCCESS(f"Hoàn thành: Phát hiện {invalid_posts_count}/{posts.count()} bài viết/sản phẩm sử dụng text thuần."))

        # 2. Quét đơn hàng đặt vé (HalinkCart)
        self.stdout.write("\n--- 2. Kiểm tra Định dạng Đơn đặt vé (HalinkCart) ---")
        carts = HalinkCart.objects.all()
        invalid_carts_count = 0
        
        for cart in carts:
            issues = []
            
            # Kiểm tra info_product
            info_prod = cart.info_product or ""
            if info_prod:
                items = info_prod.split(',')
                for idx, item in enumerate(items):
                    parts = item.split('***+++***')
                    if len(parts) < 3:
                        issues.append(f"Mục thứ {idx+1} trong info_product sai định dạng (ít hơn 3 phần tử ngăn cách bởi ***+++***): '{item}'")
            else:
                issues.append("info_product rỗng")
                
            # Kiểm tra info_user
            info_user = cart.info_user or ""
            if info_user:
                if '***+++***' not in info_user:
                    issues.append("info_user không sử dụng ký tự phân tách ***+++***")
            else:
                issues.append("info_user rỗng")
                
            if issues:
                invalid_carts_count += 1
                self.stdout.write(self.style.WARNING(
                    f"Đơn vé #{cart.Id} (Mã đơn: {cart.id_cart}): {', '.join(issues)}"
                ))
                
        self.stdout.write(self.style.SUCCESS(f"Hoàn thành: Phát hiện {invalid_carts_count}/{carts.count()} đơn vé sai định dạng."))

        # 3. Quét đơn ẩm thực và bình luận (HalinkMeta)
        self.stdout.write("\n--- 3. Kiểm tra Định dạng Dữ liệu Meta (HalinkMeta) ---")
        
        # 3.1 Đơn ẩm thực order-food
        food_orders = HalinkMeta.objects.filter(meta_type='order-food')
        invalid_food_orders = 0
        for order in food_orders:
            issues = []
            
            # Kiểm tra JSON meta_value (danh sách món)
            val = order.meta_value or ""
            if val:
                try:
                    items = json.loads(val)
                    if not isinstance(items, list):
                        issues.append("meta_value không phải là danh sách JSON")
                    else:
                        for idx, item in enumerate(items):
                            if not isinstance(item, dict) or 'id' not in item or 'qtv' not in item or 'price' not in item:
                                issues.append(f"Món thứ {idx+1} trong meta_value thiếu trường id/qtv/price")
                except json.JSONDecodeError:
                    issues.append("meta_value không phải JSON hợp lệ")
            else:
                issues.append("meta_value (danh sách món) rỗng")
                
            # Kiểm tra JSON meta_value_cus (thông tin khách)
            val_cus = order.meta_value_cus or ""
            if val_cus:
                try:
                    cus_info = json.loads(val_cus)
                    if not isinstance(cus_info, list):
                        issues.append("meta_value_cus không phải là danh sách JSON")
                    else:
                        for idx, item in enumerate(cus_info):
                            if not isinstance(item, dict) or 'name' not in item or 'value' not in item:
                                issues.append(f"Trường thứ {idx+1} trong meta_value_cus thiếu name/value")
                except json.JSONDecodeError:
                    issues.append("meta_value_cus không phải JSON hợp lệ")
            else:
                issues.append("meta_value_cus (thông tin khách) rỗng")
                
            if issues:
                invalid_food_orders += 1
                self.stdout.write(self.style.WARNING(
                    f"Đơn ẩm thực #{order.Id} (PostID: {order.Id_post}): {', '.join(issues)}"
                ))
                
        self.stdout.write(self.style.SUCCESS(f"Hoàn thành: Phát hiện {invalid_food_orders}/{food_orders.count()} đơn ẩm thực sai định dạng JSON."))

        # 3.2 Bình luận comment_post
        comments = HalinkMeta.objects.filter(meta_type='comment_post')
        invalid_comments = 0
        for comment in comments:
            issues = []
            val = comment.meta_value or ""
            if val:
                try:
                    items = json.loads(val)
                    if not isinstance(items, list):
                        issues.append("meta_value không phải là danh sách JSON")
                    else:
                        for idx, item in enumerate(items):
                            if not isinstance(item, dict) or 'name' not in item or 'value' not in item:
                                issues.append(f"Trường thứ {idx+1} trong meta_value thiếu name/value")
                except json.JSONDecodeError:
                    issues.append("meta_value không phải JSON hợp lệ")
            else:
                issues.append("meta_value rỗng")
                
            if issues:
                invalid_comments += 1
                self.stdout.write(self.style.WARNING(
                    f"Bình luận #{comment.Id} (PostID: {comment.Id_post}): {', '.join(issues)}"
                ))
                
        self.stdout.write(self.style.SUCCESS(f"Hoàn thành: Phát hiện {invalid_comments}/{comments.count()} bình luận sai định dạng JSON."))
        self.stdout.write(self.style.SUCCESS("\n=== HOÀN THÀNH QUÁ TRÌNH QUÉT ĐỐI CHIẾU DỮ LIỆU ==="))
