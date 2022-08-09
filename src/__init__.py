import os

import yaml
from flask import Flask
from werkzeug.utils import import_string


def create_app():
    """
    创建应用
    :return: 应用
    """
    # 读取yaml中的环境变量
    DEBUG = False if os.environ.get('CABITS_ENV_PATH') else True
    # DEBUG为True时, 加载本地的环境变量
    if DEBUG:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../env.yml')
    else:  # 读取configmap中的环境变量
        env_path = os.environ.get('CABITS_ENV_PATH')
    with open(env_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
    content = yaml.load(file_content, yaml.FullLoader)
    for key, value in content.items():
        if value is not None:
            print('{} =======> {}'.format(key, value))
            os.environ[key] = str(value)

    app = Flask(__name__)

    # # 初始化日志
    # from utils import ttlog
    # ttlog.create_logger(settings.log_path, 'app.log', settings.log_level)
    #
    # # Redis数据库连接初始化
    # from redis import StrictRedis
    # app.redis = StrictRedis(**app.config['REDIS'])
    #
    # # MySQL数据库连接初始化
    # from models import db
    # db.init_app(app)

    # 加载蓝图模块
    blueprints = ['src.apps.test:bp', ]
    for bp_name in blueprints:
        app.register_blueprint(import_string(bp_name))

    # 加载钩子函数
    # app.before_request(before_request)

    return app
