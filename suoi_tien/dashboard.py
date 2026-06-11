import datetime
import json
from django.utils import timezone
from suoi_tien.models import HalinkPost, HalinkUser, HalinkCart, HalinkMeta

def safe_int(val):
    if not val:
        return 0
    try:
        # Xóa các ký tự không phải số để parse an toàn
        cleaned = ''.join(c for c in str(val) if c.isdigit())
        return int(cleaned) if cleaned else 0
    except Exception:
        return 0

def dashboard_callback(request, context):
    # 1. Thống kê cơ bản
    total_users = HalinkUser.objects.count()
    total_posts = HalinkPost.objects.filter(post_type='post').count()
    total_products = HalinkPost.objects.filter(post_type='product').count()
    
    # 2. Đơn đặt vé
    total_ticket_orders = HalinkCart.objects.count()
    successful_tickets = HalinkCart.objects.filter(status=4)
    ticket_revenue = sum(c.computed_total_price_num for c in successful_tickets)
    
    # 3. Đơn ẩm thực
    total_food_orders = HalinkMeta.objects.filter(meta_type='order-food').count()
    food_revenue = sum(safe_int(m.meta_like) for m in HalinkMeta.objects.filter(meta_type='order-food'))
    
    # 4. Tương tác khác
    pending_comments_count = HalinkMeta.objects.filter(meta_type='comment_post', ticlock=1).count()
    total_support_count = HalinkMeta.objects.filter(meta_type='support').count()
    
    # 5. Danh sách đơn hàng mới nhất (5 đơn)
    recent_orders = []
    for order in HalinkCart.objects.order_by('-date')[:5]:
        # Tách thông tin user để hiển thị tên khách hàng
        user_info = order.info_user.split('***+++***')
        fullname = user_info[1] if len(user_info) > 1 else "Khách vãng lai"
        phone = user_info[2] if len(user_info) > 2 else ""
        recent_orders.append({
            'id': order.Id,
            'id_cart': order.id_cart,
            'fullname': fullname,
            'phone': phone,
            'total_price': order.computed_total_price_formatted,
            'status': order.status,
            'date': order.date
        })

    # 6. Danh sách bình luận mới nhất chờ duyệt
    recent_comments = []
    for comment in HalinkMeta.objects.filter(meta_type='comment_post', ticlock=1).order_by('-date')[:5]:
        try:
            val_data = json.loads(comment.meta_value or '[]')
            c_name = next((item.get('value') for item in val_data if item.get('name') == 'comment_name'), 'Khách ẩn danh')
            c_content = next((item.get('value') for item in val_data if item.get('name') == 'comment_content'), '')
            c_star = next((item.get('value') for item in val_data if item.get('name') == 'comment_star'), '5')
        except Exception:
            c_name = "Khách ẩn danh"
            c_content = "Không thể đọc nội dung"
            c_star = "5"
            
        recent_comments.append({
            'id': comment.Id,
            'fullname': c_name,
            'content': c_content,
            'star': c_star,
            'date': comment.date
        })

    # 7. Biểu đồ doanh thu & đơn hàng 7 ngày gần nhất
    chart_labels = []
    chart_orders = []
    chart_revenue = []
    
    for i in range(6, -1, -1):
        day = datetime.date.today() - datetime.timedelta(days=i)
        chart_labels.append(day.strftime('%d/%m'))
        
        # Thống kê đơn hàng trong ngày
        day_orders_count = HalinkCart.objects.filter(date__date=day).count()
        chart_orders.append(day_orders_count)
        
        # Doanh thu vé trong ngày
        day_success_carts = HalinkCart.objects.filter(date__date=day, status=4)
        day_rev = sum(c.computed_total_price_num for c in day_success_carts)
        chart_revenue.append(day_rev)

    # 8. Biểu đồ tình trạng đơn hàng
    status_counts = {
        '0': HalinkCart.objects.filter(status=0).count(), # Chưa thanh toán
        '1': HalinkCart.objects.filter(status=1).count(), # Đang xử lý
        '3': HalinkCart.objects.filter(status=3).count(), # Hủy/Lỗi
        '4': HalinkCart.objects.filter(status=4).count(), # Thành công
    }

    # 9. Khách dự kiến tham quan (dựa trên dateoforg)
    upcoming_tours = []
    today_str = datetime.date.today().strftime('%Y%m%d')
    for order in HalinkCart.objects.filter(dateoforg__gte=today_str).exclude(dateoforg='').order_by('dateoforg')[:5]:
        user_info = order.info_user.split('***+++***') if order.info_user else []
        fullname = user_info[1] if len(user_info) > 1 else "Khách vãng lai"
        date_formatted = f"{order.dateoforg[-2:]}/{order.dateoforg[4:6]}/{order.dateoforg[:4]}" if len(order.dateoforg) == 8 else order.dateoforg
        upcoming_tours.append({
            'date': date_formatted,
            'fullname': fullname,
            'id_cart': order.id_cart,
            'status': order.status
        })

    # 10. Danh sách nhắc việc (Yêu cầu hỗ trợ chờ duyệt)
    recent_supports = []
    for sup in HalinkMeta.objects.filter(meta_type='support').order_by('-date')[:5]:
        # Dữ liệu hỗ trợ cũ: tên - sđt - email thường lưu ở meta_title hoặc các fields rời rạc
        # Hoặc meta_value lưu text trơn. Ta parse đơn giản.
        s_name = "Khách hàng"
        if sup.meta_title:
            s_name = sup.meta_title.split('-')[0].strip() if '-' in sup.meta_title else sup.meta_title
            
        s_content = sup.meta_value if sup.meta_value else 'Cần hỗ trợ thông tin (trống nội dung)'
        recent_supports.append({
            'name': s_name,
            'phone': '', # Không tách được sđt thì để rỗng
            'content': s_content,
            'date': sup.date
        })

    # 11. Top vé bán chạy (Đọc từ giỏ hàng hiện tại)
    top_products_dict = {}
    product_price_dict = {}
    for cart in HalinkCart.objects.exclude(info_product=''):
        lines = cart.info_product.split(',')
        for line in lines:
            parts = line.split('***+++***')
            if len(parts) >= 3:
                pid = parts[0]
                try:
                    qty = int(parts[1])
                    top_products_dict[pid] = top_products_dict.get(pid, 0) + qty
                    if pid not in product_price_dict:
                        # Lưu lại giá tiền định dạng có dấu phẩy cho dễ nhìn
                        price = int(parts[2]) if parts[2].isdigit() else 0
                        product_price_dict[pid] = "{:,.0f}".format(price)
                except: pass
    top_pids = sorted(top_products_dict, key=top_products_dict.get, reverse=True)[:5]
    top_products_list = []
    for pid in top_pids:
        post = HalinkPost.objects.filter(Id=pid).first()
        if post and post.title_vn:
            title = post.title_vn
        else:
            # Ghi rõ thêm Mệnh giá vé để Admin dễ dàng tự đối chiếu
            title = f"Vé chưa cập nhật tên (Mã SP: {pid} - Mệnh giá: {product_price_dict.get(pid, '0')} đ)"
        top_products_list.append({
            'title': title,
            'qty': top_products_dict[pid]
        })

    # Cập nhật context
    context.update({
        "stats": {
            "total_users": total_users,
            "total_posts": total_posts,
            "total_products": total_products,
            "total_ticket_orders": total_ticket_orders,
            "ticket_revenue": f"{ticket_revenue:,} đ",
            "total_food_orders": total_food_orders,
            "food_revenue": f"{food_revenue:,} đ",
            "pending_comments": pending_comments_count,
            "total_support": total_support_count,
        },
        "recent_orders": recent_orders,
        "recent_comments": recent_comments,
        "chart_labels": json.dumps(chart_labels),
        "chart_orders": json.dumps(chart_orders),
        "chart_revenue": json.dumps(chart_revenue),
        "status_counts": json.dumps(list(status_counts.values())),
        "upcoming_tours": upcoming_tours,
        "recent_supports": recent_supports,
        "top_products": top_products_list,
    })
    
    return context
