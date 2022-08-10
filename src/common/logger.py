"""日志配置"""
import logging

import os
import re
import time
from logging.handlers import TimedRotatingFileHandler


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


class Log:
    @staticmethod
    def init(app_name):
        """初始化日志模块"""
        LOG_PATH = f'/cabits/logs/{app_name}/server'
        if not os.path.exists(LOG_PATH):
            os.makedirs(LOG_PATH)

        logger = logging.getLogger()  # 创建logger对象
        logger.setLevel(logging.INFO)  # 设置日志记录等级
        logging_formatter = logging.Formatter(
            '%(asctime)s %(module)s.%(funcName)s line %(lineno)d: %(message)s')  # 日志格式
        sh = logging.StreamHandler()  # 往屏幕上输出
        sh.setFormatter(logging_formatter)  # 设置屏幕上显示的格式
        logger.addHandler(sh)

        # 日志文件设置
        os.makedirs(LOG_PATH, exist_ok=True)
        file_handler = CommonTimedRotatingFileHandler(filename=f'{LOG_PATH}/{app_name}.log', when="MIDNIGHT",
                                                      interval=1, backupCount=30)
        file_handler.suffix = "%Y-%m-%d.log"
        file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
        file_handler.setFormatter(logging_formatter)  # 定义日志输出格式
        logger.addHandler(file_handler)
