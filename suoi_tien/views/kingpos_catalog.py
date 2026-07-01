import html
import json

from django.http import HttpResponse

from suoi_tien.integrations import kingpos


def kingpos_catalog_view(request):
    """
    Trang xem toàn bộ combo/vé thật bên KingPOS (ảnh, tên VN/EN, giá, mô tả) để admin
    tham khảo/copy nội dung lúc tạo sản phẩm bên CMS - KHÔNG phải để sửa gì bên KingPOS.
    """
    force_refresh = request.GET.get('refresh') == '1'
    combos = kingpos.get_combo_list(force_refresh=force_refresh)

    cards_html = ''
    if not combos:
        cards_html = (
            '<div class="empty">Không lấy được dữ liệu từ KingPOS (hệ thống đang bận/lỗi mạng). '
            'Thử bấm "Tải lại" ở góc trên.</div>'
        )
    else:
        for c in combos:
            desc = html.escape(c.get('description', ''))
            desc_en = html.escape(c.get('description_en', ''))
            img = c.get('image', '')
            img_html = (
                f'<img src="{html.escape(img)}" class="thumb" loading="lazy" '
                f'onerror="this.style.display=\'none\'">'
            ) if img else '<div class="thumb placeholder">Không có ảnh</div>'
            cards_html += f'''
<div class="card" data-name="{html.escape((c.get('name','') + ' ' + c.get('name_en','')).lower())}">
  {img_html}
  <div class="body">
    <div class="grp">{html.escape(c.get('group',''))}</div>
    <div class="name">{html.escape(c.get('name',''))}</div>
    <div class="name-en">{html.escape(c.get('name_en',''))}</div>
    <div class="price">{('{:,}'.format(int(c['price'])) + 'đ') if str(c.get('price','')).isdigit() else html.escape(str(c.get('price','')))}</div>
    <div class="mid">Mã: {html.escape(c.get('id',''))}</div>
    <details class="desc-box">
      <summary>Xem mô tả</summary>
      <div class="desc">{desc}</div>
      {f'<div class="desc-en">{desc_en}</div>' if desc_en else ''}
    </details>
    <div class="actions">
      <button type="button" class="copy-btn" onclick="kcCopy(this, {json.dumps(c.get('description',''))})">📋 Copy mô tả</button>
      <button type="button" class="copy-btn" onclick="kcCopy(this, {json.dumps(img)})" {'disabled' if not img else ''}>📋 Copy link ảnh</button>
    </div>
  </div>
</div>'''

    html_out = f'''<!DOCTYPE html>
<html lang="vi"><head>
<meta charset="UTF-8"><title>Catalog KingPOS</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Inter,sans-serif;background:#18181b;color:#e4e4e7}}
.toolbar{{position:sticky;top:0;z-index:10;display:flex;gap:8px;padding:12px 16px;background:#09090b;border-bottom:1px solid #3f3f46;align-items:center}}
.toolbar input[type=text]{{flex:1;max-width:400px;padding:8px 12px;border-radius:6px;border:1px solid #3f3f46;background:#27272a;color:#e4e4e7;font-size:13px;outline:none}}
.toolbar input[type=text]:focus{{border-color:#7c3aed}}
.toolbar a{{padding:7px 14px;border-radius:6px;background:#3f3f46;color:#e4e4e7;font-size:13px;text-decoration:none}}
.toolbar a:hover{{background:#52525b}}
.toolbar .count{{font-size:12px;color:#a1a1aa;margin-left:auto}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;padding:16px}}
.card{{background:#27272a;border:1px solid #3f3f46;border-radius:10px;overflow:hidden;display:flex;flex-direction:column}}
.thumb{{width:100%;height:140px;object-fit:cover;background:#3f3f46}}
.thumb.placeholder{{display:flex;align-items:center;justify-content:center;color:#71717a;font-size:12px}}
.body{{padding:10px 12px;display:flex;flex-direction:column;gap:4px}}
.grp{{font-size:10.5px;text-transform:uppercase;letter-spacing:.05em;color:#a78bfa}}
.name{{font-size:13.5px;font-weight:600;color:#f4f4f5}}
.name-en{{font-size:11.5px;color:#a1a1aa}}
.price{{font-size:14px;font-weight:700;color:#4ade80;margin-top:2px}}
.mid{{font-size:10.5px;color:#71717a;font-family:monospace}}
.desc-box{{margin-top:4px;font-size:11.5px;color:#d4d4d8}}
.desc-box summary{{cursor:pointer;color:#93c5fd;font-size:11.5px}}
.desc{{margin-top:6px;white-space:pre-line;line-height:1.5}}
.desc-en{{margin-top:6px;white-space:pre-line;line-height:1.5;color:#a1a1aa;border-top:1px dashed #3f3f46;padding-top:6px}}
.actions{{display:flex;gap:6px;margin-top:8px}}
.copy-btn{{flex:1;padding:6px 8px;border-radius:6px;border:1px solid #3f3f46;background:#3f3f46;color:#e4e4e7;font-size:11px;cursor:pointer}}
.copy-btn:hover{{background:#52525b}}
.copy-btn:disabled{{opacity:.4;cursor:not-allowed}}
.empty{{padding:60px 20px;text-align:center;color:#71717a}}
</style></head><body>
<div class="toolbar">
  <input type="text" id="kcSearch" placeholder="🔍 Tìm combo theo tên..." oninput="kcFilter(this.value)" autofocus>
  <a href="?refresh=1">🔄 Tải lại dữ liệu mới nhất</a>
  <span class="count" id="kcCount">{len(combos)} combo</span>
</div>
<div class="grid" id="kcGrid">{cards_html}</div>
<script>
function kcFilter(q) {{
  q = q.toLowerCase().trim();
  var cards = document.querySelectorAll('#kcGrid .card');
  var shown = 0;
  cards.forEach(function(c) {{
    var match = !q || c.dataset.name.indexOf(q) >= 0;
    c.style.display = match ? '' : 'none';
    if (match) shown++;
  }});
  document.getElementById('kcCount').innerText = shown + ' combo';
}}
function kcCopy(btn, text) {{
  if (!text) return;
  navigator.clipboard.writeText(text).then(function() {{
    var old = btn.innerText;
    btn.innerText = '✓ Đã copy';
    setTimeout(function() {{ btn.innerText = old; }}, 1200);
  }});
}}
</script>
</body></html>'''
    return HttpResponse(html_out)
