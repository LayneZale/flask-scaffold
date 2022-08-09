from flask import Blueprint
from flask_restful import Api

from . import apis
# from utils.output import output_json

bp = Blueprint('test', __name__)
api = Api(bp, catch_all_404s=True)
# api.representation('application/json')(output_json)

# 注册路由
api.add_resource(apis.TestResource, '/v1/test/codes', endpoint='TestApi')
api.add_resource(apis.MoteResource, '/v1/test/promote', endpoint='promote')
