"""
Package views cho ứng dụng Suối Tiên CMS.
Re-export để giữ tương thích ngược (core/urls.py truy cập qua suoi_tien.views.X).
"""
from .widgets_config import *   # noqa: F401,F403
from .image_browser import *    # noqa: F401,F403
from .home_sections_config import *  # noqa: F401,F403
