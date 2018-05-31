from info.modules.users import users_blue
from flask import request, abort, current_app, make_response, jsonify, session
from info.utils.captcha.captcha import *
from info import redis_store, constants, response_code, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from werkzeug.security import generate_password_hash, check_password_hash
import re, json, random, datetime


@users_blue.route('/logout')
def logout():
    """退出登入"""

    # 清除服务器的session
    try:
        session.pop('user_id', None)
        session.pop('mobile', None)
        session.pop('nick_name', None)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="清除session失败")
    return jsonify(errno=response_code.RET.OK, errmsg="退出成功!")


@users_blue.route('/login', methods=['POST'])
def login():
    """登录
    1.接受参数（手机号，密码明文）
    2.校验参数（判断参数是否齐全，手机号是否合法）
    3.使用手机号查询用户信息
    4.匹配该要登录的用户的密码
    5.更新最后一次登录的时间
    6.将状态保持数据写入到session
    7.响应登录结果
    """

    # 接受参数
    json_dict = request.json

    mobile = json_dict['mobile']
    password = json_dict['password']

    # 验证接受的参数是否齐全
    if not all([mobile, password]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    # 校验手机号格式是否正确
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号格式错误')

    # 使用手机号查询用户信息
    try:

        user = User.query.filter(User.mobile == mobile).first()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="查询用户数据失败")
    if not user:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='用户名或密码错误')
    # 验证该用户输入的密码

    if user.check_password(password):
        return jsonify(errno=response_code.RET.PWDERR, errmsg='用户名或密码错误')
    # 更新最后登入时间
    user.last_login = datetime.datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='更新最后一次登录的时间失败')

    # 将状态保持写入session
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name

    # 响应登入结果
    return jsonify(errno=response_code.RET.OK, errmsg='欢迎%s!' % user.nick_name)


@users_blue.route('/register', methods=['POST'])
def register():
    """注册
        1.接受参数（手机号，短信验证码，密码明文）
        2.校验参数（判断参数是否齐全，手机号是否合法）
        3.查询服务器存储的短信验证码
        4.跟客户端传入的短信验证码对比
        5.如果对比成功，创建User模型对象，并赋值属性
        6.同步模型对象到数据库
        7.将状态保持数据写入到session（实现注册即登录）
        8.响应注册结果
        """
    # 接受客户端提交的数据
    json_dict = request.json

    mobile = json_dict['mobile']
    smscode = json_dict['smscode']
    password = json_dict['password']

    # 验证接受的数据是否齐全
    if not all([mobile, smscode, password]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    # 校验手机号格式是否正确
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号格式错误')

    # 查询redis数据库储存的短信验证码
    try:
        smscode_server = redis_store.get('SMS' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询短信验证码失败')
    if not smscode_server:
        return jsonify(errno=response_code.RET.NODATA, errmsg='短信验证码不存在')

    # 和客户端输入的短信验证码进行判断
    if smscode_server != smscode:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='输入的短信验证码有误')

    # 创建数据库模型对象 并赋值

    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    user.password = password
    # 注册及登入 记录登入最后登入时间
    user.last_login = datetime.datetime.now()

    # 同步模型对象到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 回滚
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg="储存注册数据库失败")

    # 状态保证数据写入到session
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name

    # 响应注册结果
    return jsonify(errno=response_code.RET.OK, errmsg="注册成功")


@users_blue.route('/sms_code', methods=['POST'])
def sms_code():
    """短信验证视图"""

    # 接受参数
    jsno_str = request.data
    # jsno_str转成字典
    json_dict = json.loads(jsno_str)

    mobile = json_dict['mobile']
    image_code = json_dict['image_code']
    image_code_id = json_dict['image_code_id']

    # 校验验证码是否齐全 手机号码格式是否正确
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号格式错误')
    try:
        image_code_server = redis_store.get('imageCode:' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnp=response_code.RET.DBERR, errmsg='查询图片验证码失败')
    if not image_code_server:
        return jsonify(errnp=response_code.RET.NODATA, errmsg='图片验证码不存在')

    # 跟客户端传入的图片验证码做对比
    if image_code_server.lower() != image_code.lower():
        return jsonify(errnp=response_code.RET.PARAMERR, errmsg="输入的验证码有误")

    # 生成短信验证码 不够六位补零
    sms_code = '%06d' % random.randint(0, 999999)
    print("手机验证码:" + sms_code)

    # 调用CCP()发送短信方法
    # result = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    # if result != 0:
    #     return jsonify(errno=response_code.RET.THIRDERR, errmsg="发送短信失败")
    # 将短信验证码储存到redis数据库
    try:
        redis_store.set("SMS" + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, ermsg="储存短信验证码失败")

    return jsonify(errno=response_code.RET.OK, errmsg="发送短信验证码成功")


@users_blue.route('/image_code')
def image_code():
    # 获取参数imageCodeId
    imageCodeId = request.args.get('imageCodeId')
    # 判断imageCodeId是否为空
    if not imageCodeId:
        # 如果为空报403错误
        abort(403)

    # 生成图片验证码
    name, text, image = captcha.generate_captcha()
    print("图片验证码:" + text)
    try:
        # 将获取到的uuid和生成的验证码保存的redis数据库里
        redis_store.set('imageCode:' + imageCodeId, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    # 修改image的响应头为image/jpg
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'

    return response
