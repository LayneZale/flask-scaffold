from flask import jsonify
from flask_restful import Resource


class TestResource(Resource):
    def get(self):
        a = 1 / 0
        return jsonify({'code': 1000})
