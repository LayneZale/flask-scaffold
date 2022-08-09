import sys

from flask import Flask

from flask_restful import Api as _Api, Resource
from werkzeug.utils import import_string

from src.common.error import APIException
from src.common.error_code import ServerError
from src.common.response import my_response

app = create_app(DefaultConfig, enable_config_file=True)


# # 自定义全局异常
class Api(_Api):
    def handle_error(self, e):
        if isinstance(e, APIException):
            return e
            # 异常肯定是Exception
        else:
            # 如果是调试模式,则返回e的具体异常信息。否则返回json格式的ServerException对象！
            # 针对于异常信息，我们最好用日志的方式记录下来。
            if app.config["DEBUG"]:
                # log.error(e)
                raise e
            else:
                # log.error(e)
                return ServerError()


#
def before_request():
    """全局请求前处理函数"""
    pass





def create_app():
    """程序工厂函数"""
    app = Flask(__name__)

    # 初始化插件
    # db.init_app(app)

    # 加载蓝图模块
    blueprints = ['src.apps.users:api', ]
    for bp_name in blueprints:
        app.register_blueprint(import_string(bp_name))

    # 加载钩子函数
    app.before_request(before_request)

    return app


#
#
app = create_app()
api = Api(app)
#
# # class DemoResource(Resource):
# #     def get(self):
# #         o/1
# #         return my_response(message='get')
# #
# #     def post(self):
# #         return my_response(message='post')
# #
#
# # api.add_resource(DemoResource, '/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
