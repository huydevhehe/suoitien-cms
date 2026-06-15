"""
Package admin cho ứng dụng Suối Tiên CMS.
Import tất cả các module admin con để Django tự động phát hiện và đăng ký.
"""
from .users_admin import *      # noqa: F401,F403
from .posts_admin import *      # noqa: F401,F403
from .orders_admin import *     # noqa: F401,F403
from .options_admin import *    # noqa: F401,F403
