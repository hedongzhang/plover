#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/10/29

Author: 

Description: 

"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor

import types

ASYNC_TASK_LOCK = {}
executor = ThreadPoolExecutor(max_workers=32)
lock = threading.Lock()


class AsyncTask(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        self.lock()
        executor.submit(self.lock_wrap, *args, **kwargs)
        return kwargs.get('return_value')

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return types.MethodType(self, instance)

    def lock_wrap(self, *args, **kwargs):
        try:
            self.func(*args, **kwargs)
        except Exception as e:
            logging.exception("Async task " + self.func.__name__ + " error:" + str(e))
            raise

        finally:
            self.release()

    def lock(self):
        with lock:
            if self.func.__name__ in ASYNC_TASK_LOCK.keys():
                raise Exception("already have a same task!")
            ASYNC_TASK_LOCK[self.func.__name__] = 1
            logging.info("add lock:" + self.func.__name__)

    def release(self):
        ASYNC_TASK_LOCK.pop(self.func.__name__, None)
        logging.info("release lock:" + self.func.__name__)
