import json
from django import forms
from django.template.loader import render_to_string
from ..models import HalinkPost
from ..utils import clean_lang

class MenuBuilderWidget(forms.Textarea):
    template_name = 'admin/suoi_tien/widgets/menu_builder.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        # Lấy danh sách các trang, chuyên mục để hiển thị ở cột trái - làm sạch tiêu đề
        # (bỏ thẻ [[[:vi]]]...[[[:end_vi]]]) để không hiện chữ thẻ thô ngoài giao diện.
        pages = [
            {'Id': p['Id'], 'title_vn': clean_lang(p['title_vn'])}
            for p in HalinkPost.objects.filter(post_type='page', ticlock='0').values('Id', 'title_vn')
        ]
        post_cats = [
            {'Id': p['Id'], 'title_vn': clean_lang(p['title_vn'])}
            for p in HalinkPost.objects.filter(post_type='postcat', ticlock='0').values('Id', 'title_vn')
        ]
        product_cats = [
            {'Id': p['Id'], 'title_vn': clean_lang(p['title_vn'])}
            for p in HalinkPost.objects.filter(post_type='productcat', ticlock='0').values('Id', 'title_vn')
        ]
        
        # Load toàn bộ bài viết, chuyên mục vào map để luôn dịch được ID -> Tên
        title_map = {}
        type_map = {}
        all_posts = HalinkPost.objects.values('Id', 'title_vn', 'post_type')
        for item in all_posts:
            str_id = str(item['Id'])
            title_map[str_id] = item['title_vn'] or f"Bài viết {str_id}"
            type_map[str_id] = item['post_type'] or 'unknown'
            
        context['pages'] = pages
        context['post_cats'] = post_cats
        context['product_cats'] = product_cats
        context['title_map'] = json.dumps(title_map)
        context['type_map'] = json.dumps(type_map)
        
        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return render_to_string(self.template_name, context)
