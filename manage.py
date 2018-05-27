from info import create_app, db
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from info import models  # 导入models 让manage知道models的存在

# 创建app 传参给create_app函数
app = create_app('dev')

# 创建脚本管理器对象
manager = Manager(app)

# 让迁移和app和db建立关系
Migrate(app, db)

# 将迁移数据库脚本命令添加到manager
manager.add_command('mysql', MigrateCommand)

if __name__ == '__main__':
    print(app.url_map)

    manager.run()
