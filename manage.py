from info import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# 创建app 传参给create_app函数
app = create_app('dev')

# 创建脚本管理器对象
manager = Manager(app)

# 将迁移数据库脚本命令添加到manager
manager.add_command('mysql', MigrateCommand)


@app.route("/")
def index():
    from flask import session

    session['name'] = 'abc'

    return "index"


if __name__ == '__main__':
    manager.run()
