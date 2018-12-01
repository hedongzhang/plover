#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/10/29

Author: 

Description: 

"""

import json
from concurrent.futures import ThreadPoolExecutor

import tornado.web

from conf import config
from utiles.exception import ParameterInvalidException
from utiles import xml

executor = ThreadPoolExecutor(max_workers=32)

RESPONSE_STATUS_SUCESS = 200
RESPONSE_MESSAGE_SUCESS = "请求成功"

RESPONSE_STATUS_REQUEST_ERROR = 400
RESPONSE_MESSAGE_REQUEST_ERRER = "Request Error: {error_message}"

RESPONSE_STATUS_SERVER_ERROR = 500
RESPONSE_MESSAGE_SERVER_ERROR = "Server Error: {error_message}"

CALLBACK_RESPONSE_SUCESS_CODE = "SUCCESS"
CALLBACK_RESPONSE_SUCESS_MSG = "OK"

CALLBACK_RESPONSE_ERROR_CODE = "FAIL"
CALLBACK_RESPONSE_ERROR_MSG = ""


class BasicHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.session_id = ""
        super(BasicHandler, self).__init__(application, request, **kwargs)

    def set_default_headers(self):
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    def response(self, data=None, status=RESPONSE_STATUS_SUCESS, message=RESPONSE_MESSAGE_SUCESS):
        if not data:
            data = dict()
        return_request = dict(status=status, message=message, data=data)
        self.write(return_request)

    def response_request_error(self, message):
        status = RESPONSE_STATUS_REQUEST_ERROR
        message = RESPONSE_MESSAGE_REQUEST_ERRER.format(error_message=message)
        self.response(status, message)

    def response_server_error(self, message):
        status = RESPONSE_STATUS_SERVER_ERROR
        message = RESPONSE_MESSAGE_SERVER_ERROR.format(error_message=message)
        self.response(status, message)

    def request_args(self, necessary_list=None):
        try:
            request_context = json.loads(self.request.body)
        except Exception as e:
            raise ParameterInvalidException("JSON解析失败")

        self.session_id = request_context.get("session_id")
        request_args = request_context.get("post_vars")

        if necessary_list:
            for args in necessary_list:
                if args not in request_args:
                    raise ParameterInvalidException("请求缺少必要的参数")

        return request_args

    def data_received(self, chunk):
        pass


class CallbackHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.session_id = ""
        super(CallbackHandler, self).__init__(application, request, **kwargs)

    def set_default_headers(self):
        self.set_header("Content-Type", "application/xml; charset=UTF-8")

    def response(self, return_code=CALLBACK_RESPONSE_SUCESS_CODE, return_msg=CALLBACK_RESPONSE_SUCESS_MSG):
        response_args = dict(return_code=return_code, return_msg=return_msg)
        self.write(xml.dumps(response_args))

    def response_error(self, message):
        self.response(CALLBACK_RESPONSE_ERROR_CODE, message)

    def request_args(self, necessary_list=None):
        try:
            request_args = xml.loads(self.request.body)
        except Exception as e:
            raise ParameterInvalidException("parse callback request args failed!")

        if necessary_list:
            for args in necessary_list:
                if args not in request_args:
                    raise ParameterInvalidException("请求缺少必要的参数")

        return request_args

    def data_received(self, chunk):
        pass


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

    def data_received(self, chunk):
        pass


class StaticHandler(tornado.web.StaticFileHandler):
    def __init__(self, application, request, **kwargs):
        kwargs['path'] = config.get("static_path")
        super(StaticHandler, self).__init__(application, request, **kwargs)

    def data_received(self, chunk):
        pass
