"""自定义异常"""
import json

from flask import request
from werkzeug.exceptions import HTTPException


class APIException(HTTPException):
    """
    为了使代码简洁, 首先定义一个最基本的类, 供其它类继承, 这个自定义的APIException继承HTTPException.
    1. 为了返回特定的body信息, 需要重写get_body;
    2. 为了指定返回类型, 需要重写get_headers.
    3. 为了接收自定义的参数, 重写了__init__;
    4. 同时定义了类变量作为几个默认参数.(code表示http状态码，error_code表示自定义异常code)
    """
    code = 200
    message = '服务器未知错误'
    error_code = 5000

    # 自定义需要返回的信息，在初始化完成并交给父类
    def __init__(self, message=None, code=None, error_code=None):
        if code:
            self.code = code
        if message:
            self.message = message
        if error_code:
            self.error_code = error_code
        super(APIException, self).__init__(message, None)

    def get_body(self, environ=None, scope=None):
        body = dict(
            code=self.error_code,
            message=self.message
        )
        # sort_keys 取消排序规则，ensure_ascii 中文显示
        text = json.dumps(body, sort_keys=False, ensure_ascii=False)
        return text

    def get_headers(self, environ=None, scope=None):
        """Get a list of headers."""
        return [('Content-Type', 'application/json')]

    @staticmethod
    def get_url_no_parm():
        full_path = str(request.path)
        return full_path


class LogicErrorFailed(Exception):
    """logic错误类"""

    def __init__(self, detail):
        self.detail = detail


class ValidationErrFailed(Exception):
    """验证器错误类"""

    def __init__(self, detail):
        self.detail = detail
