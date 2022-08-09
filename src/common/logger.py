"""日志配置"""
import logging

import os
import time
from logging.config import dictConfig
from logging.handlers import TimedRotatingFileHandler

from src.main import app

LOG_PATH = f'/cabits/logs/{app.name}/server'
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)


class CommonTimedRotatingFileHandler(TimedRotatingFileHandler):

    @property
    def dfn(self):
        currentTime = int(time.time())
        # get the time that this sequence started at and make it a TimeTuple
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.rotation_filename(self.baseFilename + "." + time.strftime(self.suffix, timeTuple))

        return dfn

    def shouldRollover(self, record):
        """
        是否应该执行日志滚动操作：
        1、存档文件已存在时，执行滚动操作
        2、当前时间 >= 滚动时间点时，执行滚动操作
        """
        dfn = self.dfn
        t = int(time.time())
        if t >= self.rolloverAt or os.path.exists(dfn):
            return 1
        return 0

    def doRollover(self):
        """
        执行滚动操作
        1、文件句柄更新
        2、存在文件处理
        3、备份数处理
        4、下次滚动时间点更新
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple

        dfn = self.dfn

        # 存档log 已存在处理
        if not os.path.exists(dfn):
            self.rotate(self.baseFilename, dfn)

        # 备份数控制
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)

        # 延迟处理
        if not self.delay:
            self.stream = self._open()

        # 更新滚动时间点
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval

        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            dstNow = time.localtime(currentTime)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


LOG_CONF = LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # 格式配置
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(module)s.%(funcName)s line %(lineno)d: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'verbose': {
            'format': ('%(asctime)s %(levelname)s [%(process)d-%(threadName)s] '
                       '%(module)s.%(funcName)s line %(lineno)d: %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S',
        }
    },
    # Handler 配置
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple'
        },
        'my_handler': {
            'class': 'CommonTimedRotatingFileHandler',
            'filename': f'{LOG_PATH}/{app.name}.log',  # 日志保存路径
            'when': 'midnight',  # 每天凌晨零点切割日志
            'backupCount': 30,  # 日志保留 30 天
            'formatter': 'verbose',
            "encoding": "utf8"
        },

    },
    # Logger 配置
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'inf': {
            'handlers': ['my_handler', 'console'],
            'propagate': True,
            'level': 'INFO',
        },
        'err': {
            # 'handlers': ['my_handler', 'console', 'mail_admin'],
            'handlers': ['my_handler', 'console'],
            'propagate': True,
            'level': 'ERROR',
        },
        'cri': {
            # 'handlers': ['my_handler', 'console', 'mail_admin'],
            'handlers': ['my_handler', 'console'],
            'propagate': True,
            'level': 'CRITICAL',
        }
    }
}

dictConfig(LOG_CONF)
cri_log = logging.getLogger('cri')  # 重要
err_log = logging.getLogger('err')  # 警告
info_log = logging.getLogger('inf')  # 提示
g_acc_log = logging.getLogger('gunicorn.access')  # gunicorn access
g_err_log = logging.getLogger('gunicorn.error')  # gunicorn error
