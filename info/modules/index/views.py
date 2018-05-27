from info.modules.index import index_blue
from flask import render_template, current_app
from info import redis_store


@index_blue.route("/")
def index():
    """主页视图"""
    return render_template('news/index.html')


@index_blue.route('/favicon.ico')
def favicon():
    """加载title图标视图"""
    return current_app.send_static_file('news/favicon.ico')
