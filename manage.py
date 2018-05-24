from info import create_app

# 创建app 传参给create_app函数
app = create_app('pro')


@app.route("/")
def index():
    from flask import session

    session['name'] = 'abc'

    return "index"


if __name__ == '__main__':
    app.run()
