"""gunicorn的配置"""
import os

from main import app

LOG_PATH = f'/cabits/logs/{app.name}/gunicorn'
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

bind = ["0.0.0.0:8000"]
daemon = True  # 是否开启守护进程模式
pidfile = '/opt/logs/gunicorn.pid'
workers = 3  # 工作进程数量
worker_class = "uvicorn.workers.UvicornWorker"  # 指定一个异步处理的库(websocket)
# worker_class = "gevent"                           # 指定一个异步处理的库(一般情况)
# worker_class = "egg:meinheld#gunicorn_worker"   # 比 gevent 更快的一个异步网络库
worker_connections = 65535  # 单个进程的最大连接数
max_requests = 1000  # 到达一定请求数重启worker防止内存泄漏
max_requests_jitter = 50  # 重启防抖（50的偏移量）
keepalive = 60  # 服务器，能够避免频繁的三次握手过程
timeout = 6000
graceful_timeout = 10
forwarded_allow_ips = '*'

# 日志处理
# capture_output = True
# loglevel = 'info'
# access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(D)s ms %({authorization}i)s'
# errorlog = '/cabits/logs/error-log/{}-error.log'.format(time.strftime("%Y%m%d", time.localtime()))
# accesslog = '/cabits/logs/access-log/{}-access.log'.format(time.strftime("%Y%m%d", time.localtime()))
logconfig_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    # 格式配置
    'formatters': {
        'generic': {
            'format': '%(asctime)s %(levelname)s %(module)s.%(funcName)s line %(lineno)d: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        }
    },
    # Handler 配置
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'generic'
        },
        'gunicorn_error': {
            'class': 'common.log.CommonTimedRotatingFileHandler',
            'filename': f'{LOG_PATH}/error.log',  # 日志保存路径
            'when': 'midnight',  # 每天凌晨零点切割日志
            'backupCount': 30,  # 日志保留 30 天
            'formatter': 'generic',
            "encoding": "utf8"
        },
        'gunicorn_access': {
            'class': 'common.log.CommonTimedRotatingFileHandler',
            'filename': f'{LOG_PATH}/access.log',  # 日志保存路径
            'when': 'midnight',  # 每天凌晨零点切割日志
            'backupCount': 30,  # 日志保留 30 天
            'formatter': 'generic',
            "encoding": "utf8"
        },
    },
    # Logger 配置
    'loggers': {
        'gunicorn.error': {
            "level": "ERROR",
            "handlers": ["gunicorn_error"],
            "propagate": False,
            "qualname": "gunicorn.error"
        },
        'gunicorn.access': {
            "level": "INFO",
            "handlers": ["gunicorn_access"],
            "propagate": False,
            "qualname": "gunicorn.access"
        }
    }
}
