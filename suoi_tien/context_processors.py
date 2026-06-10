from .models import HalinkMeta

def cms_counts(request):
    if request.user.is_authenticated:
        # Bình luận chưa duyệt (ticlock = '1')
        pending_comments = HalinkMeta.objects.filter(meta_type='comment_post', ticlock='1').count()
        # Số hỗ trợ mới (ticlock = '1' hoặc tất cả hỗ trợ)
        pending_support = HalinkMeta.objects.filter(meta_type='support', ticlock='1').count()
        if pending_support == 0:
            # Nếu không lọc được theo ticlock, đếm tổng số hỗ trợ chưa xử lý (hoặc lấy số lượng tương tác hỗ trợ)
            pending_support = HalinkMeta.objects.filter(meta_type='support').count()
        
        return {
            'pending_comments_count': pending_comments,
            'pending_support_count': pending_support,
        }
    return {
        'pending_comments_count': 0,
        'pending_support_count': 0,
    }
