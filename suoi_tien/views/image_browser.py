import os
from django.views.decorators.csrf import csrf_exempt

# ==============================================================================
# IMAGE BROWSER VIEW
# ==============================================================================

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'}


@csrf_exempt
def image_browser_view(request):
    """
    Popup trình duyệt ảnh - liệt kê tất cả ảnh từ thư mục uploads.
    Hỗ trợ tải lên ảnh trực tiếp từ máy để phục vụ kiểm thử.
    Params: field_id = id input cần gán, subfolder = thư mục con (mặc định: hinhanh)
    """
    from django.conf import settings
    from django.http import HttpResponse, HttpResponseRedirect
    from django.utils.text import get_valid_filename

    field_id  = request.GET.get('field_id', request.POST.get('field_id', 'id_post_image'))
    subfolder = request.GET.get('subfolder', request.POST.get('subfolder', 'hinhanh'))
    search    = request.GET.get('q', '').lower().strip()
    multi     = request.GET.get('multi', request.POST.get('multi', '')) == '1'

    image_dir = os.path.join(settings.MEDIA_ROOT, subfolder)

    # Xử lý tải file lên nếu là POST request
    if request.method == 'POST' and request.FILES.getlist('upload_files'):
        uploaded_files = request.FILES.getlist('upload_files')
        allowed_exts = IMAGE_EXTENSIONS | {'.swf', '.flv', '.mp4'}
        os.makedirs(image_dir, exist_ok=True)
        
        for uploaded_file in uploaded_files:
            fname = get_valid_filename(uploaded_file.name)
            ext = os.path.splitext(fname)[1].lower()

            if ext in allowed_exts:
                target_path = os.path.join(image_dir, fname)

                # Tránh ghi đè file trùng tên
                base, ext = os.path.splitext(fname)
                counter = 1
                while os.path.exists(target_path):
                    fname = f"{base}_{counter}{ext}"
                    target_path = os.path.join(image_dir, fname)
                    counter += 1

                with open(target_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

        # Redirect lại về GET để tránh reload submit lại form
        multi_param = "&multi=1" if multi else ""
        return HttpResponseRedirect(f"{request.path}?field_id={field_id}&subfolder={subfolder}{multi_param}")

    images = []
    if os.path.isdir(image_dir):
        allowed_exts = IMAGE_EXTENSIONS | {'.swf', '.flv', '.mp4'}
        for fname in sorted(os.listdir(image_dir), reverse=True):
            ext = os.path.splitext(fname)[1].lower()
            if ext in allowed_exts:
                if search and search not in fname.lower():
                    continue
                rel_path = f"{subfolder}/{fname}"
                url = f"{settings.MEDIA_URL}{rel_path}"
                images.append({'path': rel_path, 'url': url, 'name': fname})

    click_attr = "toggleImage(this, '{name}')" if multi else "selectImage('{path}', '{name}')"

    img_grid = ""
    if images:
        for img in images:
            onclick = click_attr.format(path=img["path"], name=img["name"])
            # Nếu là file video hoặc flash, hiển thị hình đại diện tương ứng
            ext = os.path.splitext(img['name'])[1].lower()
            if ext in {'.swf', '.flv', '.mp4'}:
                thumb_url = "https://placehold.co/120x120/1e1b4b/e0e7ff?text=FILE"
                img_grid += (
                    f'<div class="img-item" data-name="{img["name"]}" onclick="{onclick}">'
                    f'<img src="{thumb_url}" alt="{img["name"]}">'
                    f'<div class="name">{img["name"]}</div>'
                    f'</div>'
                )
            else:
                img_grid += (
                    f'<div class="img-item" data-name="{img["name"]}" onclick="{onclick}">'
                    f'<img src="{img["url"]}" alt="{img["name"]}" loading="lazy"'
                    f' onerror="this.src=\'https://placehold.co/120x120/27272a/71717a?text=Err\'">'
                    f'<div class="name">{img["name"]}</div>'
                    f'</div>'
                )
    else:
        img_grid = '<div class="empty">Không tìm thấy ảnh nào.</div>'

    multi_hidden = '<input type="hidden" name="multi" value="1">' if multi else ""
    done_btn = '<button type="button" class="done-btn" onclick="finishMultiSelect()" style="display:none" id="doneBtn">Xong (<span id="selCount">0</span>)</button>' if multi else ""

    html = f"""<!DOCTYPE html>
<html lang="vi"><head>
<meta charset="UTF-8"><title>Chọn file</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Inter,sans-serif;background:#ffffff;color:#18181b}}
.toolbar{{position:sticky;top:0;z-index:10;display:flex;gap:8px;padding:10px 14px;background:#f4f4f5;border-bottom:1px solid #e4e4e7;align-items:center}}
.toolbar input[type=text]{{flex:1;padding:6px 10px;border-radius:6px;border:1px solid #e4e4e7;background:#ffffff;color:#18181b;font-size:13px;outline:none}}
.toolbar input[type=text]:focus{{border-color:#7c3aed}}
.toolbar button{{padding:6px 14px;border-radius:6px;border:none;background:#7c3aed;color:#fff;font-size:13px;cursor:pointer}}
.toolbar button:hover{{background:#6d28d9}}
.upload-btn{{padding:6px 14px;border-radius:6px;background:#10b981;color:#fff;font-size:13px;cursor:pointer;white-space:nowrap;display:inline-block}}
.upload-btn:hover{{background:#059669}}
.done-btn{{padding:6px 14px;border-radius:6px;border:none;background:#7c3aed;color:#fff;font-size:13px;cursor:pointer;white-space:nowrap}}
.done-btn:hover{{background:#6d28d9}}
.count{{font-size:12px;color:#71717a;align-self:center;white-space:nowrap}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px;padding:12px}}
.img-item{{position:relative;border-radius:8px;overflow:hidden;border:1px solid #e4e4e7;cursor:pointer;background:#f4f4f5;aspect-ratio:1;transition:border-color .15s,transform .15s}}
.img-item:hover{{border-color:#7c3aed;transform:scale(1.03)}}
.img-item.selected{{border:3px solid #7c3aed;box-shadow:0 0 0 2px #ddd6fe}}
.img-item .order-badge{{position:absolute;top:4px;right:4px;background:#7c3aed;color:#fff;font-size:11px;font-weight:bold;border-radius:50%;width:20px;height:20px;display:flex;align-items:center;justify-content:center}}
.img-item img{{width:100%;height:100%;object-fit:cover;display:block}}
.img-item .name{{position:absolute;bottom:0;left:0;right:0;background:rgba(255,255,255,.9);color:#18181b;font-size:10px;padding:3px 5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.empty{{text-align:center;padding:60px 20px;color:#71717a}}

/* Dark Mode Styles */
@media (prefers-color-scheme: dark) {{
  body{{background:#18181b;color:#e4e4e7}}
  .toolbar{{background:#09090b;border-bottom:1px solid #3f3f46}}
  .toolbar input[type=text]{{border:1px solid #3f3f46;background:#27272a;color:#e4e4e7}}
  .img-item{{border:1px solid transparent;background:#27272a}}
  .img-item .name{{background:rgba(0,0,0,.7);color:#e4e4e7}}
}}
</style></head><body>
<div class="toolbar">
  <form method="get" style="display:flex;flex:1;gap:8px;">
    <input type="hidden" name="field_id" value="{field_id}">
    <input type="hidden" name="subfolder" value="{subfolder}">
    {multi_hidden}
    <input type="text" name="q" placeholder="Tìm theo tên file..." value="{search}" autofocus>
    <button type="submit">Tìm</button>
  </form>
  <form method="post" enctype="multipart/form-data" style="display:flex;align-items:center;">
    <input type="hidden" name="field_id" value="{field_id}">
    <input type="hidden" name="subfolder" value="{subfolder}">
    {multi_hidden}
    <label class="upload-btn">
      Tải lên
      <input type="file" name="upload_files" multiple onchange="this.form.submit()" accept="image/*,application/x-shockwave-flash,video/*" style="display:none;">
    </label>
  </form>
  {done_btn}
  <span class="count">{len(images)} file</span>
</div>
<div class="grid">{img_grid}</div>
<script>
function selectImage(path, name) {{
  if (window.opener && window.opener.receiveImageFromBrowser) {{
    window.opener.receiveImageFromBrowser('{field_id}', path, name);
    window.close();
  }}
}}

// Chế độ chọn nhiều ảnh: click để chọn/bỏ chọn, không đóng popup ngay
var selectedNames = [];
function toggleImage(el, name) {{
  var idx = selectedNames.indexOf(name);
  if (idx === -1) {{
    selectedNames.push(name);
    el.classList.add('selected');
    var badge = document.createElement('div');
    badge.className = 'order-badge';
    badge.innerText = selectedNames.length;
    el.appendChild(badge);
  }} else {{
    selectedNames.splice(idx, 1);
    el.classList.remove('selected');
    var badge = el.querySelector('.order-badge');
    if (badge) badge.remove();
    // Renumber các badge còn lại
    document.querySelectorAll('.img-item.selected').forEach(function (item) {{
      var n = item.getAttribute('data-name');
      var i = selectedNames.indexOf(n);
      var b = item.querySelector('.order-badge');
      if (b) b.innerText = i + 1;
    }});
  }}
  var doneBtn = document.getElementById('doneBtn');
  var selCount = document.getElementById('selCount');
  if (selCount) selCount.innerText = selectedNames.length;
  if (doneBtn) doneBtn.style.display = selectedNames.length > 0 ? 'inline-block' : 'none';
}}

function finishMultiSelect() {{
  if (window.opener && window.opener.receiveImagesFromBrowser && selectedNames.length > 0) {{
    window.opener.receiveImagesFromBrowser('{field_id}', selectedNames);
    window.close();
  }}
}}
</script>
</body></html>"""

    return HttpResponse(html)
