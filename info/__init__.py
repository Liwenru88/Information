from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from Config import configs

# 创建SQLAlchemy对象
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)

    # 配置文件加载
    app.config.from_object(configs[config_name])

    # 创建连接到Redis数据库对象
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)

    # 开启CSRF保护
    CSRFProtect(app)

    # 配置flask_session,将session数据写入到服务器的redis数据库
    Session(app)

    # 把app传给db
    db.init_app(app)

    return app
