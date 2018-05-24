from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect


class Config(object):
    """配置文件类"""

    # 配置秘钥:项目中的CSRF和session会用到
    SECRET_KEY = "5I35e4Y6IUrBiEETcwO/eWrJ/Zxl5EbfBp8gHqxE9qQHgqmu" + \
                 "OnHr2w6zijnMGYdDPrURJSolj9GtFGFmcbg5ZdJnMhx1OqZqI0L" + \
                 "9AtoGnvlCWUwe0RFzWJEekoubjopmQhrgyZkCU3RMzDM9uWM=AWdGPTL3BsIHGSseRvEZ+Wjk"

    # 开启调试模式
    DEBUG = True

    # 配置mysql数据库连接
    SQLALCHEMY_DATABASE_URI = "msyql://root:123@192.168.76.140:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置Redis数据库连接
    REDIS_HOST = "192.168.76.140"
    REDIS_PORT = 6379

    # 指定session数据存储在redis
    SESSION_TYPE = "redis"
    # 告诉sessio redis数据库服务器的位置
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 是否将session签名后再储存
    SESSION_USE_SIGNER = True
    # 当SESSION_PERMANENT为True时，设置session的有效期才可以成立，正好默认就是True
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 7


app = Flask(__name__)

app.config.from_object(Config)

# 创建SQLAlchemy对象
db = SQLAlchemy(app)

# 创建连接到Redis数据库对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# 开启CSRF保护
CSRFProtect(app)

# 配置flask_session,将session数据写入到服务器的redis数据库
Session(app)


@app.route("/")
def index():
    from flask import session

    session['name'] = 'abc'

    return "index"


if __name__ == '__main__':
    app.run()
