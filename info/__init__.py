from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from Config import configs
from logging.handlers import RotatingFileHandler
import logging


def setup_log(level):
    # 设置 志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建 志记录 ，指明 志保存的 径、每个 志 件的最   、保存的 志 件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100,
                                           backupCount=10)  # 创建 志记录的格式  志等级 输  志信息的 件名  数  志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的 志记录 设置 志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的 志 具对象(flask app使 的)添加 志记录
    logging.getLogger().addHandler(file_log_handler)


# Redis空连接
redis_store = None

# 创建SQLAlchemy对象
db = SQLAlchemy()


def create_app(config_name):
    setup_log(configs[config_name].LOGGING_LEVEL)

    app = Flask(__name__)

    # 配置文件加载
    app.config.from_object(configs[config_name])

    global redis_store
    # 创建连接到Redis数据库对象
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)

    # 开启CSRF保护
    CSRFProtect(app)

    # 配置flask_session,将session数据写入到服务器的redis数据库
    Session(app)

    # 把app传给db
    db.init_app(app)

    # 在哪里注册就在哪里导包
    from info.modules.index import index_blue
    from info.modules.users import users_blue
    # 将蓝图注册到app
    app.register_blueprint(index_blue)
    app.register_blueprint(users_blue)

    return app
