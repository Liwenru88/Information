from redis import StrictRedis
import logging


class Config(object):
    """配置文件类"""

    # 配置秘钥:项目中的CSRF和session会用到
    SECRET_KEY = "5I35e4Y6IUrBiEETcwO/eWrJ/Zxl5EbfBp8gHqxE9qQHgqmu" + \
                 "OnHr2w6zijnMGYdDPrURJSolj9GtFGFmcbg5ZdJnMhx1OqZqI0L" + \
                 "9AtoGnvlCWUwe0RFzWJEekoubjopmQhrgyZkCU3RMzDM9uWM=AWdGPTL3BsIHGSseRvEZ+Wjk"

    # 开启调试模式
    DEBUG = True

    # 配置mysql数据库连接
    SQLALCHEMY_DATABASE_URI = "msyql://root:123@192.168.76.110:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置Redis数据库连接
    REDIS_HOST = "192.168.76.110"
    REDIS_PORT = 6379

    # 指定session数据存储在redis
    SESSION_TYPE = "redis"
    # 告诉sessio redis数据库服务器的位置
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 是否将session签名后再储存
    SESSION_USE_SIGNER = True
    # 当SESSION_PERMANENT为True时，设置session的有效期才可以成立，正好默认就是True
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 7


class DevelopmentConfig(Config):
    """开发环境下的配置"""

    # 开发环境下的日志等级警告
    LOGGING_LEVEL = logging.DEBUG

    pass


class ProductionConfig(Config):
    """生产环境下的配置 最终上线的配置"""

    # 生产环境下日志等级警告
    LOGGING_LEVEL = logging.WARN

    # 生产环境关闭调试模式
    DEBUG = False

    # 生产模式下的MySQL数据库连接
    SQLALCHEMY_DATABASE_URI = "msyql://root:123@192.168.76.110:3306/information"


class UnittestConfig(Config):
    """测试环境下的配置"""

    # 测试环境下等级警告
    LOGGING_LEVEL = logging.DEBUG

    # 开启测试模式
    TESTING = True

    # 测试模式模式下的MySQL数据库连接
    SQLALCHEMY_DATABASE_URI = "msyql://root:123@192.168.76.110:3306/information"


configs = {
    'dev': DevelopmentConfig,
    'pro': ProductionConfig,
    'uni': UnittestConfig
}
