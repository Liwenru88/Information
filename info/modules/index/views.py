from info.modules.index import index_blue
from flask import render_template
from info import redis_store


@index_blue.route("/")
def index():
    return render_template('news/index.html')
