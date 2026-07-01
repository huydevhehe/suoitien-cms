import html
import json

from django import forms
from django.utils.safestring import mark_safe

from suoi_tien.integrations import kingpos


class KingposComboPickerWidget(forms.HiddenInput):
    """
    Ô chọn 1 combo THẬT bên hệ thống vé KingPOS (tìm kiếm theo tên, danh sách lấy
    trực tiếp từ API /v1/combo, cache 10 phút - xem suoi_tien/integrations/kingpos.py).
    Lưu vào field dạng chuỗi (chỉ id combo, VD "6797"), tên chỉ để hiển thị lại lúc sửa.
    """
    is_hidden = False

    def render(self, name, value, attrs=None, renderer=None):
        field_id = (attrs or {}).get('id', 'id_%s' % name)
        hidden_input = super().render(name, value, attrs, renderer)

        combos = kingpos.get_combo_list()

        display_name = ''
        if value:
            match = kingpos.find_combo_by_id(value)
            if match:
                display_name = '%s (Mã %s)' % (match['name'], match['id'])
            else:
                display_name = 'Mã %s (không tra được tên - KingPOS có thể đang lỗi)' % value

        combos_json = json.dumps(combos, ensure_ascii=False).replace('</', '<\\/')

        html_out = '''
<div class="kingpos-picker-wrap" style="position:relative;max-width:460px;">
  <input type="text" id="%(fid)s_display" class="kingpos-picker-display" readonly value="%(display)s"
    placeholder="-- Chưa chọn combo KingPOS --" onclick="kposToggle('%(fid)s')"
    style="cursor:pointer;width:100%%;box-sizing:border-box;padding:8px 10px;border-radius:6px;">
  <div id="%(fid)s_dropdown" class="kingpos-picker-dropdown" style="display:none;position:absolute;top:100%%;left:0;right:0;z-index:9999;border-radius:6px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,.35);">
    <input type="text" class="kingpos-picker-search" placeholder="🔍 Tìm combo theo tên..." oninput="kposFilter('%(fid)s', this.value)"
      style="width:100%%;box-sizing:border-box;padding:8px 10px;border:none;outline:none;font-size:12px;">
    <div id="%(fid)s_list" class="kingpos-picker-list" style="max-height:220px;overflow-y:auto;"></div>
  </div>
  %(empty_warn)s
  <a href="/admin/suoi_tien/kingpos-catalog/" target="_blank" style="font-size:11px;color:#93c5fd;display:inline-block;margin-top:4px;">👁 Xem toàn bộ combo KingPOS (ảnh, mô tả đầy đủ, copy nội dung)</a>
</div>
%(hidden_input)s
<style>
.kingpos-picker-display{background:#fff;color:#111827;border:1px solid #d1d5db;}
.dark .kingpos-picker-display{background:rgb(24 24 27);color:#f4f4f5;border-color:rgb(63 63 70);}
.kingpos-picker-dropdown{background:#fff;border:1px solid #d1d5db;}
.dark .kingpos-picker-dropdown{background:#18181b;border-color:#3f3f46;}
.kingpos-picker-search{background:#f9fafb;color:#111827;border-bottom:1px solid #e5e7eb!important;}
.dark .kingpos-picker-search{background:#27272a;color:#e4e4e7;border-bottom:1px solid #3f3f46!important;}
.kingpos-picker-item{padding:7px 10px;cursor:pointer;font-size:12.5px;color:#111827;border-bottom:1px solid #f3f4f6;}
.dark .kingpos-picker-item{color:#e4e4e7;border-bottom:1px solid #27272a;}
.kingpos-picker-item:hover{background:#f3e8ff;}
.dark .kingpos-picker-item:hover{background:#312e81;}
.kingpos-picker-item .grp{font-size:10.5px;opacity:.6;margin-left:6px;}
.kingpos-picker-empty{padding:10px;font-size:12px;color:#9ca3af;}
</style>
<script>
if (!window._kposReady) {
  window._kposReady = true;
  window._kposReg = {};

  window.kposRenderList = function(fieldId, q) {
    var reg = window._kposReg[fieldId];
    if (!reg) return;
    var list = document.getElementById(fieldId + '_list');
    if (!list) return;
    var ql = (q || '').trim().toLowerCase();
    var filtered = ql ? reg.combos.filter(function(c) {
      return c.name.toLowerCase().indexOf(ql) >= 0 || String(c.id).toLowerCase().indexOf(ql) >= 0;
    }) : reg.combos;
    if (!filtered.length) {
      list.innerHTML = '<div class="kingpos-picker-empty">Không tìm thấy combo nào (hoặc KingPOS chưa trả dữ liệu).</div>';
      return;
    }
    list.innerHTML = '';
    filtered.forEach(function(c) {
      var item = document.createElement('div');
      item.className = 'kingpos-picker-item';
      item.innerHTML = c.name + ' - ' + (c.price ? Number(c.price).toLocaleString('vi-VN') + 'đ' : '') + '<span class="grp">' + (c.group || '') + '</span>';
      item.addEventListener('mousedown', function(e) {
        e.preventDefault();
        window.kposSelect(fieldId, c.id, c.name);
      });
      list.appendChild(item);
    });
  };

  window.kposCloseAll = function() {
    document.querySelectorAll('.kingpos-picker-dropdown').forEach(function(el) { el.style.display = 'none'; });
  };

  window.kposToggle = function(fieldId) {
    var dd = document.getElementById(fieldId + '_dropdown');
    var display = document.getElementById(fieldId + '_display');
    if (!dd || !display) return;
    var opening = dd.style.display === 'none';
    window.kposCloseAll();
    if (opening) {
      // Gắn thẳng vào <body> + định vị theo toạ độ thật của ô input, tránh bị
      // các khung cha có overflow:hidden (Unfold hay dùng cho hiệu ứng thu gọn) cắt mất.
      if (dd.parentElement !== document.body) document.body.appendChild(dd);
      var rect = display.getBoundingClientRect();
      dd.style.position = 'fixed';
      dd.style.top = rect.bottom + 'px';
      dd.style.left = rect.left + 'px';
      dd.style.width = rect.width + 'px';
      dd.style.right = 'auto';
      dd.style.display = 'block';
      window.kposRenderList(fieldId, '');
    }
  };

  window.addEventListener('scroll', window.kposCloseAll, true);
  window.addEventListener('resize', window.kposCloseAll);

  window.kposFilter = function(fieldId, q) { window.kposRenderList(fieldId, q); };

  window.kposSelect = function(fieldId, id, name) {
    var hidden = document.getElementById(fieldId);
    var display = document.getElementById(fieldId + '_display');
    if (hidden) hidden.value = id;
    if (display) display.value = name + ' (Mã ' + id + ')';
    var dd = document.getElementById(fieldId + '_dropdown');
    if (dd) dd.style.display = 'none';
  };

  document.addEventListener('mousedown', function(e) {
    // Dropdown được đẩy ra <body> khi mở (xem kposToggle), nên "trong picker" giờ
    // tính cả .kingpos-picker-wrap (ô hiển thị) lẫn .kingpos-picker-dropdown (đã tách ra ngoài).
    var inside = e.target.closest && (e.target.closest('.kingpos-picker-wrap') || e.target.closest('.kingpos-picker-dropdown'));
    if (!inside) window.kposCloseAll();
  });
}
window._kposReg['%(fid)s'] = { combos: %(combos_json)s };
</script>''' % {
            'display': html.escape(display_name),
            'fid': field_id,
            'hidden_input': hidden_input,
            'combos_json': combos_json,
            'empty_warn': (
                '<div style="font-size:11px;color:#92400e;margin-top:4px;">'
                '⚠️ Không lấy được danh sách combo từ KingPOS lúc tải trang (có thể do hệ thống đang bận/lỗi mạng). '
                'Thử tải lại trang.</div>'
            ) if not combos else '',
        }
        return mark_safe(html_out)
