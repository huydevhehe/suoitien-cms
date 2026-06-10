import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ..models import HalinkPost, TicketOrderProxy, FoodOrderProxy
from ..utils import paginate_queryset
from .dashboard import parse_ticket_products, parse_ticket_user

# --- Helper Functions for Food Orders ---

def parse_food_items(meta_value_str):
    if not meta_value_str or meta_value_str == "None":
        return []
    try:
        data = json.loads(meta_value_str)
        items = []
        for item in data:
            p_id = item.get('id')
            try:
                qty = int(item.get('qtv', 1))
            except (ValueError, TypeError):
                qty = 1
            try:
                price = float(item.get('price', 0))
            except ValueError:
                price = 0.0
            post = HalinkPost.objects.filter(Id=p_id).first() if p_id else None
            title = post.title_vn if post else f"Món ăn #{p_id}"
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
    except Exception:
        return []

# --- Views ---

@login_required(login_url='admin_login')
def ticket_orders(request):
    raw_orders = TicketOrderProxy.objects.order_by('-date')
    page_obj = paginate_queryset(request, raw_orders, 20)
    
    orders_data = []
    for o in page_obj:
        user_info = parse_ticket_user(o.info_user)
        items = parse_ticket_products(o.info_product)
        
        total_price = 0.0
        if o.total_price_final and o.total_price_final != 'None' and o.total_price_final.strip():
            try:
                total_price = float(o.total_price_final)
            except ValueError:
                pass
        if total_price == 0.0 and items:
            total_price = sum(item['total'] for item in items)
            
        orders_data.append({
            'Id': o.Id,
            'id_cart': o.id_cart,
            'fullname': user_info.get('fullname', 'Khách vãng lai'),
            'phone': user_info.get('phone', ''),
            'email': user_info.get('email', ''),
            'address': user_info.get('address', ''),
            'note': user_info.get('note', ''),
            'items': items,
            'total_price': total_price,
            'date': o.date,
            'status': o.status
        })
        
    context = {
        'orders': orders_data,
        'page_obj': page_obj,
        'active_menu': 'ticket_orders'
    }
    return render(request, 'admin_fe/ticket_orders.html', context)

@login_required(login_url='admin_login')
def food_orders(request):
    raw_orders = FoodOrderProxy.objects.filter(meta_type='order-food').order_by('-date')
    page_obj = paginate_queryset(request, raw_orders, 20)
    
    orders_data = []
    for o in page_obj:
        customer_info = o.get_customer_info()
        fullname = o.fullname
        phone = o.phone
        address = o.address
        note = ""
        for item in customer_info:
            if item.get('name') == 'ghichu':
                note = item.get('value', '')
                
        items = parse_food_items(o.meta_value)
        try:
            total_price = float(o.meta_like) if o.meta_like else 0.0
        except ValueError:
            total_price = sum(item['total'] for item in items)
            
        orders_data.append({
            'Id': o.Id,
            'fullname': fullname or "Khách đặt món",
            'phone': phone,
            'address': address,
            'note': note,
            'items': items,
            'total_price': total_price,
            'date': o.date,
            'ticlock': o.ticlock
        })
        
    context = {
        'orders': orders_data,
        'page_obj': page_obj,
        'active_menu': 'food_orders'
    }
    return render(request, 'admin_fe/food_orders.html', context)
