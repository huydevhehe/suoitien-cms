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


def send_email_via_smtp_proxy(to_email, subject, body_html):
    """
    Gửi email bằng cách đọc cấu hình SMTP động từ SMTPProxy (nếu có).
    Nếu không có, fallback về cấu hình mặc định trong settings của Django.
    """
    from suoi_tien.models import SMTPProxy
    from django.core.mail import get_connection, EmailMultiAlternatives
    from django.core.mail.backends.smtp import EmailBackend
    
    # Lấy cấu hình từ database
    configs = {x.meta_title: x.meta_value for x in SMTPProxy.objects.all() if x.meta_title}
    
    host = configs.get('smtp_host') or configs.get('host')
    port = configs.get('smtp_port') or configs.get('port')
    username = configs.get('smtp_user') or configs.get('username') or configs.get('smtp_username')
    password = configs.get('smtp_pass') or configs.get('password') or configs.get('smtp_password')
    secure = configs.get('smtp_secure') or configs.get('secure') or 'ssl'
    from_email = configs.get('smtp_email') or configs.get('from_email') or username
    
    if not host or not username or not password:
        # Fallback về connection mặc định của Django
        connection = get_connection()
        from_email = from_email or 'no-reply@suoitien.vn'
    else:
        try:
            port = int(port)
        except (TypeError, ValueError):
            port = 465 if secure == 'ssl' else 587
            
        use_tls = (secure == 'tls')
        use_ssl = (secure == 'ssl')
        
        connection = EmailBackend(
            host=host,
            port=port,
            username=username,
            password=password,
            use_tls=use_tls,
            use_ssl=use_ssl,
            timeout=10
        )
        
    msg = EmailMultiAlternatives(
        subject=subject,
        body="Vui lòng mở email bằng trình duyệt hỗ trợ HTML.",
        from_email=from_email,
        to=[to_email],
        connection=connection
    )
    msg.attach_alternative(body_html, "text/html")
    msg.send()

