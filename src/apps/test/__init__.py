from flask import Blueprint

from response import Api
from . import apis

# from utils.output import output_json


bp = Blueprint('test', __name__)
api = Api(bp)
# 注册路由
api.add_resource(apis.TestResource, '/api/v1/test', endpoint='TestApi')
