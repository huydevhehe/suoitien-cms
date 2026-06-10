from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import HalinkMeta, CommentProxy, SupportProxy
from ..utils import paginate_queryset

@login_required(login_url='admin_login')
def comment_list(request):
    comments_qs = CommentProxy.objects.filter(meta_type='comment_post').order_by('-date')
    page_obj = paginate_queryset(request, comments_qs, 20)

    # Sử dụng thuộc tính processed_data của CommentProxy đã refactor
    comments_data = [c.processed_data for c in page_obj]

    context = {
        'comments': comments_data,
        'page_obj': page_obj,
        'active_menu': 'comments'
    }
    return render(request, 'admin_fe/comment_list.html', context)

@login_required(login_url='admin_login')
def toggle_comment_status(request, pk):
    comment = get_object_or_404(HalinkMeta, Id=pk, meta_type='comment_post')
    if comment.ticlock == 0 or comment.ticlock == '0':
        comment.ticlock = 1
        messages.success(request, "Đã ẩn bình luận thành công.")
    else:
        comment.ticlock = 0
        messages.success(request, "Đã duyệt bình luận thành công.")
    comment.save()
    return redirect('comment_list')

@login_required(login_url='admin_login')
def reply_comment(request, pk):
    if request.method == 'POST':
        comment = get_object_or_404(HalinkMeta, Id=pk, meta_type='comment_post')
        reply_text = request.POST.get('reply_text', '').strip()
        comment.meta_value_cus = reply_text if reply_text else 'None'
        comment.save()
        messages.success(request, "Đã lưu phản hồi bình luận.")
    return redirect('comment_list')

@login_required(login_url='admin_login')
def support_list(request):
    supports_qs = SupportProxy.objects.filter(meta_type='support').order_by('-date')
    page_obj = paginate_queryset(request, supports_qs, 20)
    context = {
        'supports': page_obj,
        'page_obj': page_obj,
        'active_menu': 'support'
    }
    return render(request, 'admin_fe/support_list.html', context)

@login_required(login_url='admin_login')
def toggle_support_status(request, pk):
    support = get_object_or_404(HalinkMeta, Id=pk, meta_type='support')
    if support.ticlock == 0 or support.ticlock == '0':
        support.ticlock = 1
    else:
        support.ticlock = 0
    support.save()
    messages.success(request, "Đã cập nhật trạng thái yêu cầu hỗ trợ.")
    return redirect('support_list')
