from info.modules.users import users_blue
from flask import request, abort, current_app, make_response, jsonify
from info.utils.captcha.captcha import *
from info import redis_store, constants, response_code
from info.libs.yuntongxun.sms import CCP
import re
import json
import random


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
        print("图片验证码:"+image_code_server)
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
    print("手机验证码:"+sms_code)

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
