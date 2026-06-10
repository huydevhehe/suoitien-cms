import re

def clean_lang(text):
    """
    Hàm bóc tách ngôn ngữ từ chuỗi định dạng của CMS cũ:
    [[[:vi]]]Tiêu đề tiếng Việt[[[:end_vi]]][[[:en]]]English Title[[[:end_en]]]
    """
    if not text:
        return ""
    if not isinstance(text, str):
        return text
        
    # Tìm kiếm nội dung tiếng Việt
    vi_match = re.search(r'\[\[\[:vi\]\]\](.*?)\[\[\[:end_vi\]\]\]', text, re.DOTALL)
    if vi_match:
        return vi_match.group(1).strip()
        
    # Nếu không có tiếng Việt, tìm tiếng Anh làm fallback
    en_match = re.search(r'\[\[\[:en\]\]\](.*?)\[\[\[:end_en\]\]\]', text, re.DOTALL)
    if en_match:
        return en_match.group(1).strip()
        
    # Nếu có các thẻ ngôn ngữ khác nhưng không phải vi/en, loại bỏ toàn bộ thẻ và trả về
    if '[[[:' in text:
        cleaned = re.sub(r'\[\[\[:[a-z_]+\]\]\]|\[\[\[:end_[a-z_]+\]\]\]', '', text)
        return cleaned.strip()
        
    return text.strip()


def paginate_queryset(request, queryset, per_page=20):
    """
    Helper function dùng chung để phân trang cho QuerySet
    """
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
