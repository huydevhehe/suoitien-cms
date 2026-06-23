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

    image_dir = os.path.join(settings.MEDIA_ROOT, subfolder)

    # Xử lý tải file lên nếu là POST request
    if request.method == 'POST' and request.FILES.get('upload_file'):
        uploaded_file = request.FILES['upload_file']
        fname = get_valid_filename(uploaded_file.name)
        ext = os.path.splitext(fname)[1].lower()

        # Hỗ trợ cả ảnh và các file flash/video thông dụng
        allowed_exts = IMAGE_EXTENSIONS | {'.swf', '.flv', '.mp4'}
        if ext in allowed_exts:
            os.makedirs(image_dir, exist_ok=True)
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
            return HttpResponseRedirect(f"{request.path}?field_id={field_id}&subfolder={subfolder}")

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

    img_grid = ""
    if images:
        for img in images:
            # Nếu là file video hoặc flash, hiển thị hình đại diện tương ứng
            ext = os.path.splitext(img['name'])[1].lower()
            if ext in {'.swf', '.flv', '.mp4'}:
                thumb_url = "https://placehold.co/120x120/1e1b4b/e0e7ff?text=FILE"
                img_grid += (
                    f'<div class="img-item" onclick="selectImage(\'{img["path"]}\', \'{img["name"]}\')">'
                    f'<img src="{thumb_url}" alt="{img["name"]}">'
                    f'<div class="name">{img["name"]}</div>'
                    f'</div>'
                )
            else:
                img_grid += (
                    f'<div class="img-item" onclick="selectImage(\'{img["path"]}\', \'{img["name"]}\')">'
                    f'<img src="{img["url"]}" alt="{img["name"]}" loading="lazy"'
                    f' onerror="this.src=\'https://placehold.co/120x120/27272a/71717a?text=Err\'">'
                    f'<div class="name">{img["name"]}</div>'
                    f'</div>'
                )
    else:
        img_grid = '<div class="empty">Không tìm thấy ảnh nào.</div>'

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
.count{{font-size:12px;color:#71717a;align-self:center;white-space:nowrap}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px;padding:12px}}
.img-item{{position:relative;border-radius:8px;overflow:hidden;border:1px solid #e4e4e7;cursor:pointer;background:#f4f4f5;aspect-ratio:1;transition:border-color .15s,transform .15s}}
.img-item:hover{{border-color:#7c3aed;transform:scale(1.03)}}
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
    <input type="text" name="q" placeholder="Tìm theo tên file..." value="{search}" autofocus>
    <button type="submit">Tìm</button>
  </form>
  <form method="post" enctype="multipart/form-data" style="display:flex;align-items:center;">
    <input type="hidden" name="field_id" value="{field_id}">
    <input type="hidden" name="subfolder" value="{subfolder}">
    <label class="upload-btn">
      Tải lên
      <input type="file" name="upload_file" onchange="this.form.submit()" accept="image/*,application/x-shockwave-flash,video/*" style="display:none;">
    </label>
  </form>
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
</script>
</body></html>"""

    return HttpResponse(html)
