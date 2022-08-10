import logging

from flask import jsonify
from flask_restful import Resource


class TestResource(Resource):
    def get(self):
        logging.info('hello')
        return jsonify({'code': 1000})
