from info.modules.index import index_blue
from flask import render_template, current_app, session, request, jsonify, template_rendered
from info.models import User, News
from info import constants, response_code


@index_blue.route('/news_list')
def news_list():
    """主页新闻展示"""
    # 接受参数
    cid = request.args.get('cid', '1')
    page = request.args.get('page')
    per_page = request.args.get('per_page')
    # 校验参数
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PWDERR, errmsg="参数错误")
    # 获取数据库新闻数据
    if cid == 1:
        try:
            paginate = News.query.order_by(News.create_time.desc()).paginate(page, per_page, False)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg="查询新闻数据出错")
    else:
        try:
            paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page,
                                                                                                             per_page,
                                                                                                             False)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg="查询新闻数据出错")

    news_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page

    news_dict_List = []
    for news in news_list:
        news_dict_List.append(news.to_basic_dict())

    data = {
        'news_dict_List': news_dict_List,
        'total_page': total_page,
        'current_page': current_page
    }

    return jsonify(errno=response_code.RET.OK, errmsg="OK", data=data)


@index_blue.route("/")
def index():
    """主页视图"""
    # 显示登入信息
    user_id = session.get('user_id', None)
    user = None
    User.avatar_url
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 获取新闻排行数据
    news_clicks = None
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    context = {
        'user': user,
        'news_clicks': news_clicks
    }

    return render_template('news/index.html', context=context)


@index_blue.route('/favicon.ico')
def favicon():
    """加载title图标视图"""
    return current_app.send_static_file('news/favicon.ico')
