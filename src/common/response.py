"""自定义成功response"""

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
