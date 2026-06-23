"""
Package admin cho ứng dụng Suối Tiên CMS.
Import tất cả các module admin con để Django tự động phát hiện và đăng ký.
"""
from .users_admin import *      # noqa: F401,F403
from .site_config_admin import *     # noqa: F401,F403
from .content_admin import *         # noqa: F401,F403
from .ticket_orders_admin import *   # noqa: F401,F403
from .food_orders_admin import *     # noqa: F401,F403
from .interactions_admin import *    # noqa: F401,F403
from .site_settings_admin import *   # noqa: F401,F403
