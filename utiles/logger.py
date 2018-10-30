#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/10/29

Author: 

Description: 

"""

import logging
import logging.handlers


class Logger(object):
    def __init__(self, level=logging.INFO):
        self.level = level
        self._logger = logging.getLogger()
        logging.getLogger("requests").setLevel(logging.WARNING)
        formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
        stdout_handle = logging.StreamHandler()
        stdout_handle.setFormatter(formatter)
        self._logger.addHandler(stdout_handle)

        file_handle = logging.handlers.RotatingFileHandler('./log/plover.log', maxBytes=20 * 1024 * 1024, backupCount=5)
        file_handle.setFormatter(formatter)
        self._logger.addHandler(file_handle)

        self._logger.setLevel(level)
        # 把原先的logger对象的函数info、debug等替换掉，当传进入的错误信息中有回车，会在每个回车前多加一些空格，以便打印的好看一些
        function_list = ['info', 'debug', 'warning', 'error', 'critical', 'exception']
        for function_name in function_list:
            setattr(self._logger, function_name, getattr(self._logger, function_name))

    def debug(self, msg):
        self._logger.debug(msg)

    def info(self, msg):
        self._logger.info(msg)

    def warning(self, msg, **kwargs):
        self._logger.warning(msg, **kwargs)

    def error(self, msg):
        self._logger.error(msg)

    def critical(self, msg):
        self._logger.critical(msg)

    def fatal(self, msg):
        self._logger.critical(msg)

    @staticmethod
    def exception(msg="exception"):
        logging.exception(msg)

logger = Logger(level=logging.INFO)


def debug(msg):
    logger.debug(msg)


def info(msg):
    logger.info(msg)


def warn(msg, **kwargs):
    logger.warning(msg, **kwargs)


def error(msg):
    logger.error(msg)


def critical(msg):
    logger.critical(msg)


def fatal(msg):
    logger.critical(msg)


def exception(msg="exception"):
    logging.exception(msg)
