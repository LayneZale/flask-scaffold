from werkzeug.utils import import_string


def create_flask_app(config, enable_config_file=False):
    """
    创建Flask应用
    :param config: 配置信息对象
    :param enable_config_file: 是否允许运行环境中的配置文件覆盖已加载的配置信息
    :return: Flask应用
    """
    app = Flask(__name__)
    app.config.from_object(config)
    if enable_config_file:
        from . import constants
        app.config.from_envvar(constants.GLOBAL_SETTING_ENV_NAME, silent=True)

    return app


def create_app(config, enable_config_file=False):
    """
    创建应用
    :param config: 配置信息对象
    :param enable_config_file: 是否允许运行环境中的配置文件覆盖已加载的配置信息
    :return: 应用
    """
    app = create_flask_app(config, enable_config_file)

    # 初始化日志
    from utils import ttlog
    ttlog.create_logger(settings.log_path, 'app.log', settings.log_level)

    # Redis数据库连接初始化
    from redis import StrictRedis
    app.redis = StrictRedis(**app.config['REDIS'])

    # MySQL数据库连接初始化
    from models import db
    db.init_app(app)

    # 创建APScheduler定时任务调度器对象
    executors = {
        'default': ThreadPoolExecutor(10)
    }

    app.scheduler = BackgroundScheduler(executors=executors)

    # 添加"静态的"定时任务
    from .schedule.statistic import fix_statistics
    app.scheduler.add_job(fix_statistics, 'interval', seconds=2, args=[app])

    # 启动定时任务调度器
    app.scheduler.start()

    # 添加请求钩子
    from utils.middlewares import jwt_authentication, long_query
    app.before_request(jwt_authentication)
    app.after_request(long_query)

    # 注册蓝图
    from .resources.test import test_bp
    app.register_blueprint(test_bp)

    from .resources.web import web_bp
    app.register_blueprint(web_bp)

    # 加载蓝图模块
    blueprints = ['src.apps.test:bp', ]
    for bp_name in blueprints:
        app.register_blueprint(import_string(bp_name))

    # 加载钩子函数
    app.before_request(before_request)

    return app
