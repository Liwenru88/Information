from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    """配置文件类"""

    # 开启调试模式
    DEBUG = True

    # 配置mysql数据库连接
    SQLALCHEMY_DATABASE_URI = "msyql://root:123@192.168.76.140:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)


@app.route("/")
def index():
    return "index"


if __name__ == '__main__':
    app.run()
