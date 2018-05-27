from info.modules.users import users_blue
from flask import request, abort, current_app, make_response, jsonify
from info.utils.captcha.captcha import *
from info import redis_store, constants, response_code
import re
import json


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
    if not re.match(r'^((13[0-9])|(14[5|7])|(15([0-3]|[5-9]))|(18[0,5-9]))\\d{8}$', mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号格式错误')
    try:
        image_code_server = redis_store.get('ImageCode:' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errnp=response_code.RET.DBERR, errmsg='查询图片验证码失败')
    if not image_code_server:
        return jsonify(errnp=response_code.RET.NODATA, errmsg='图片验证码不存在')

    #


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
