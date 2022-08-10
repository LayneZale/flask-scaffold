"""自定义response"""
import os


from common.error import APIException
from common.error_code import ServerError

from flask_restful import Api as _Api


# 自定义全局异常
class Api(_Api):
    def handle_error(self, e):
        if isinstance(e, APIException):
            return e
            # 异常肯定是Exception
        else:
            # 如果是调试模式,则返回e的具体异常信息。否则返回json格式的ServerException对象！
            # 针对于异常信息，我们最好用日志的方式记录下来。
            if not os.environ.get('CABITS_ENV_PATH'):
                # log.error(e)
                raise e
            else:
                # log.error(e)
                return ServerError()


def my_response(message='成功', code=1000, data=None):
    """自定义response"""
    response = {
        'code': code,
        'message': message,
        'data': data
    }
    if data is None:
        del response['data']
    return response
