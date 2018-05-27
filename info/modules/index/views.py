from info.modules.index import index_blue


@index_blue.route("/")
def index():
    return "index"
