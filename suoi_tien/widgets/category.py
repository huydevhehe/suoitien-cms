from django import forms
import re
from django.utils.safestring import mark_safe


class CategoryCheckboxWidget(forms.Widget):
    """
    Widget chọn chuyên mục dạng hộp sổ xuống (dropdown collapsible) chứa checkbox.
    Tự động cập nhật nhãn đã chọn và hỗ trợ giao diện tối/sáng của Unfold.
    """

    def __init__(self, category_type='postcat', exclude_id=None, *args, **kwargs):
        self.category_type = category_type
        self.exclude_id = exclude_id
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        from ..models import HalinkPost

        qs = HalinkPost.objects.filter(post_type=self.category_type)
        if hasattr(self, 'exclude_id') and self.exclude_id:
            qs = qs.exclude(Id=self.exclude_id)
        categories = qs.order_by('sort', 'Id')

        selected_ids = []
        if value:
            selected_ids = [v.strip() for v in str(value).strip(',').split(',') if v.strip()]

        rows = []
        for cat in categories:
            cat_id = str(cat.Id)
            checked = 'checked' if cat_id in selected_ids else ''

            raw_title = cat.title_vn or f'ID: {cat_id}'
            vi_match = re.search(r'\[\[\[:vi\]\]\](.*?)\[\[\[:end_vi\]\]\]', raw_title, re.DOTALL)
            title = vi_match.group(1).strip() if vi_match else re.sub(r'\[\[\[:[^\]]+\]\]\]', '', raw_title).strip()

            indent = '&nbsp;&nbsp;&nbsp;— ' if cat.idcat else ''

            rows.append(
                '<label class="cat-item">'
                '<input type="checkbox" name="%s" value="%s" %s>'
                '<span>%s%s</span>'
                '</label>' % (name, cat_id, checked, indent, title)
            )

        inner = '\n'.join(rows) if rows else '<p style="color:#888;font-size:13px;padding:8px 12px;">Chưa có chuyên mục nào.</p>'

        html = """
<div class="category-dropdown-container" id="cat_container_%s">
  <div class="category-dropdown-header" onclick="toggleCategoryDropdown('cat_container_%s')">
    <span class="category-dropdown-selected-text">Chọn chuyên mục...</span>
    <span class="material-symbols-outlined dropdown-arrow">expand_more</span>
  </div>
  <div class="category-dropdown-panel">
    <div class="category-checkbox-widget">
      %s
    </div>
  </div>
</div>

<style>
.category-dropdown-container {
    position: relative;
    width: 100%%;
    max-width: 480px;
}
.category-dropdown-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    color: #1f2937;
    user-select: none;
    transition: all 0.15s;
}
.dark .category-dropdown-header {
    background: rgb(24 24 27);
    border-color: rgb(63 63 70);
    color: #f4f4f5;
}
.category-dropdown-header:hover {
    border-color: #9ca3af;
}
.dark .category-dropdown-header:hover {
    border-color: #52525b;
}
.category-dropdown-panel {
    display: none;
    position: absolute;
    top: 100%%;
    left: 0;
    width: 100%%;
    margin-top: 4px;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    z-index: 999;
}
.dark .category-dropdown-panel {
    background: rgb(24 24 27);
    border-color: rgb(63 63 70);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
}
.category-dropdown-container.open .category-dropdown-panel {
    display: block;
}
.category-dropdown-container.open .dropdown-arrow {
    transform: rotate(180deg);
}
.dropdown-arrow {
    transition: transform 0.2s;
    font-size: 18px;
    color: #6b7280;
}
.dark .dropdown-arrow {
    color: #a1a1aa;
}
.category-checkbox-widget {
    max-height: 220px;
    overflow-y: auto;
    padding: 8px 10px;
}
.category-checkbox-widget .cat-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 4px;
    cursor: pointer;
    color: #1f2937;
    font-size: 13px;
    transition: background 0.15s;
}
.dark .category-checkbox-widget .cat-item {
    color: #e5e7eb;
}
.category-checkbox-widget .cat-item:hover {
    background: #f3f4f6;
}
.dark .category-checkbox-widget .cat-item:hover {
    background: #27272a;
}
.category-checkbox-widget input[type="checkbox"] {
    accent-color: #7c3aed;
    width: 16px;
    height: 16px;
    flex-shrink: 0;
}
</style>

<script>
if (!window._categoryDropdownReady) {
  window._categoryDropdownReady = true;

  window.toggleCategoryDropdown = function(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const isOpen = container.classList.contains('open');

    // Close other dropdowns
    document.querySelectorAll('.category-dropdown-container').forEach(c => {
      c.classList.remove('open');
    });

    if (!isOpen) {
      container.classList.add('open');
    }
  };

  // Click outside to close
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.category-dropdown-container')) {
      document.querySelectorAll('.category-dropdown-container').forEach(c => {
        c.classList.remove('open');
      });
    }
  });

  // Update dropdown text based on checkbox status
  window.updateCategorySelectedText = function(container) {
    const checkedBoxes = container.querySelectorAll('input[type="checkbox"]:checked');
    const textSpan = container.querySelector('.category-dropdown-selected-text');
    if (!textSpan) return;

    if (checkedBoxes.length === 0) {
      textSpan.textContent = 'Chọn chuyên mục...';
      textSpan.style.color = '';
    } else {
      const names = [];
      checkedBoxes.forEach(cb => {
        let labelText = cb.nextElementSibling.textContent;
        labelText = labelText.replace(/^[\\s —-]+/, '');
        names.push(labelText);
      });
      textSpan.textContent = names.join(', ');
      textSpan.style.color = '#a78bfa'; // Violet tone matching dark/light mode
    }
  };

  // Bind event
  document.addEventListener('change', function(e) {
    if (e.target.matches('.category-checkbox-widget input[type="checkbox"]')) {
      const container = e.target.closest('.category-dropdown-container');
      if (container) {
        window.updateCategorySelectedText(container);
      }
    }
  });
}

// Perform initial setup for this container
(function() {
  const container = document.getElementById('cat_container_%s');
  if (container) {
    window.updateCategorySelectedText(container);
  }
})();
</script>
""" % (name, name, inner, name)

        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        values = data.getlist(name)
        if values:
            return ','.join(values) + ','
        return ''
