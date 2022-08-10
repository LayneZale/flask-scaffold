"""错误的code码"""
from common.error import APIException


class ServerError(APIException):
    message = '服务器未知错误'
    error_code = 5000


class UserError(APIException):
    message = '用户错误'
    error_code = 1001
