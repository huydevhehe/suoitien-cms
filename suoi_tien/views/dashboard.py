import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from ..models import HalinkPost, HalinkCart, HalinkUser, HalinkMeta

# --- Helper Functions for Dashboard ---

def parse_ticket_products(info_product_str):
    """
    Parses "6275***+++***4***+++***400000,6276***+++***2***+++***199000"
    """
    if not info_product_str or info_product_str == "None":
        return []
    items = []
    for item in info_product_str.split(','):
        if not item.strip():
            continue
        parts = item.split('***+++***')
        if len(parts) >= 3:
            p_id = parts[0]
            try:
                qty = int(parts[1])
            except ValueError:
                qty = 0
            try:
                price = float(parts[2])
            except ValueError:
                price = 0.0
            # Query post info
            post = HalinkPost.objects.filter(Id=p_id).first() if p_id else None
            title = post.title_vn if post else f"Sản phẩm #{p_id}"
            image = post.post_image if post else ""
            items.append({
                'product_id': p_id,
                'quantity': qty,
                'price': price,
                'product_title': title,
                'product_image': image,
                'total': qty * price
            })
    return items

def parse_ticket_user(info_user_str):
    """
    Parses "null***+++***Sơn Trần Hồ***+++***1228081687***+++***tranhoson1991@gmail.com***+++***87, Chế Lan Viên..."
    """
    if not info_user_str or info_user_str == "None":
        return {}
    parts = info_user_str.split('***+++***')
    return {
        'fullname': parts[1] if len(parts) > 1 else '',
        'phone': parts[2] if len(parts) > 2 else '',
        'email': parts[3] if len(parts) > 3 else '',
        'address': parts[4] if len(parts) > 4 else '',
        'note': parts[5] if len(parts) > 5 else ''
    }

# --- Views ---

def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Tài khoản của bạn không có quyền truy cập quản trị.")
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không chính xác.")
            
    return render(request, 'admin_fe/login.html')

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

@login_required(login_url='admin_login')
def admin_dashboard(request):
    # Statistics counts
    total_orders = HalinkCart.objects.count()
    total_customers = HalinkUser.objects.count()
    total_categories = HalinkPost.objects.filter(post_type__in=['productcat', 'postcat']).count()
    total_posts = HalinkPost.objects.filter(post_type='post').count()

    # Get recent ticket orders
    raw_tickets = HalinkCart.objects.order_by('-date')[:5]
    recent_tickets = []
    for t in raw_tickets:
        user_info = parse_ticket_user(t.info_user)
        items = parse_ticket_products(t.info_product)
        total_price = 0.0
        if t.total_price_final and t.total_price_final != 'None' and t.total_price_final.strip():
            try:
                total_price = float(t.total_price_final)
            except ValueError:
                pass
        if total_price == 0.0 and items:
            total_price = sum(item['total'] for item in items)
        
        recent_tickets.append({
            'id_cart': t.id_cart,
            'fullname': user_info.get('fullname', 'Khách vãng lai'),
            'phone': user_info.get('phone', ''),
            'total_price': total_price,
            'date': t.date,
            'status': t.status
        })

    # Get recent food orders
    raw_foods = HalinkMeta.objects.filter(meta_type='order-food').order_by('-date')[:5]
    recent_foods = []
    for f in raw_foods:
        customer_data = f.meta_value_cus
        fullname = ""
        phone = ""
        if customer_data:
            try:
                cus_json = json.loads(customer_data)
                for item in cus_json:
                    if item.get('name') == 'fullname':
                        fullname = item.get('value')
                    elif item.get('name') == 'phone':
                        phone = item.get('value')
            except Exception:
                pass
        
        try:
            total_price = float(f.meta_like) if f.meta_like else 0.0
        except ValueError:
            total_price = 0.0
            
        recent_foods.append({
            'Id': f.Id,
            'Id_post': f.Id_post,
            'fullname': fullname or "Khách đặt món",
            'phone': phone,
            'total_price': total_price,
            'date': f.date,
            'ticlock': f.ticlock
        })

    # Prepare chart data for last 7 days (Ticket & Food Sales)
    labels = []
    ticket_sales = []
    food_sales = []
    
    for i in range(6, -1, -1):
        day = timezone.now().date() - timedelta(days=i)
        labels.append(day.strftime('%d/%m'))
        
        # Calculate tickets sales for this day
        day_tickets = HalinkCart.objects.filter(date__date=day)
        t_sum = 0.0
        for dt in day_tickets:
            val = 0.0
            if dt.total_price_final and dt.total_price_final != 'None' and dt.total_price_final.strip():
                try:
                    val = float(dt.total_price_final)
                except ValueError:
                    pass
            if val == 0.0:
                items = parse_ticket_products(dt.info_product)
                val = sum(item['total'] for item in items)
            t_sum += val
        ticket_sales.append(t_sum)
        
        # Calculate food sales for this day
        day_foods = HalinkMeta.objects.filter(meta_type='order-food', date__date=day)
        f_sum = 0.0
        for df in day_foods:
            try:
                f_sum += float(df.meta_like) if df.meta_like else 0.0
            except ValueError:
                pass
        food_sales.append(f_sum)

    context = {
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_categories': total_categories,
        'total_posts': total_posts,
        'recent_tickets': recent_tickets,
        'recent_foods': recent_foods,
        'chart_labels': json.dumps(labels),
        'chart_ticket_sales': json.dumps(ticket_sales),
        'chart_food_sales': json.dumps(food_sales),
        'active_menu': 'dashboard'
    }
    return render(request, 'admin_fe/dashboard.html', context)
