from flask import Blueprint

# 创建用户模块蓝图
users_blue = Blueprint('users', __name__,url_prefix="/users")

from . import views
