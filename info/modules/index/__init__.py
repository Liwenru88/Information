from flask import Blueprint

# 创建主页蓝图
index_blue = Blueprint('index', __name__)

# 导入views
from . import views
