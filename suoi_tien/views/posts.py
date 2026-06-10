from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from ..models import PostProxy, ProductProxy
from ..utils import paginate_queryset

@login_required(login_url='admin_login')
def post_list(request):
    query = request.GET.get('q', '')
    posts_qs = PostProxy.objects.filter(post_type='post').order_by('-Id')
    if query:
        posts_qs = posts_qs.filter(Q(title_vn__icontains=query) | Q(description_vn__icontains=query))
    
    page_obj = paginate_queryset(request, posts_qs, 20)
    context = {
        'posts': page_obj,
        'page_obj': page_obj,
        'query': query,
        'active_menu': 'posts'
    }
    return render(request, 'admin_fe/post_list.html', context)

@login_required(login_url='admin_login')
def product_list(request):
    query = request.GET.get('q', '')
    products_qs = ProductProxy.objects.filter(post_type='product').order_by('sort')
    if query:
        products_qs = products_qs.filter(Q(title_vn__icontains=query) | Q(description_vn__icontains=query))
    
    page_obj = paginate_queryset(request, products_qs, 20)
    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'query': query,
        'active_menu': 'products'
    }
    return render(request, 'admin_fe/product_list.html', context)
