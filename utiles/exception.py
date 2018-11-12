#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/10/29

Author: 

Description: 

"""


class PlException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ParameterInvalidException(PlException):
    def __str__(self):
        return "参数错误：" + self.message

if __name__ == "__main__":
    try:
        raise PlException("hello error")
    except PlException as e:
        print("error: {e}, message: {message}".format(e=e, message=e.message))
