from info.modules.index import index_blue
from info import redis_store


@index_blue.route("/")
def index():
    redis_store.set('name', '哈哈哈')

    return "index"
