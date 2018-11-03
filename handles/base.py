#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/10/29

Author: 

Description: 

"""

import json

import tornado.web

from utiles import config

from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=32)

RESPONSE_STATUS_SUCESS = 200
RESPONSE_MESSAGE_SUCESS = "请求成功"

RESPONSE_STATUS_BAD_REQUEST = 400
RESPONSE_MESSAGE_BAD_REQUEST = "错误请求：无效的请求参数"

RESPONSE_STATUS_SERVER_ERROR = 500
RESPONSE_MESSAGE_SERVER_ERROR = "后端服务错误: {error_message}"


class BasicHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.session_id = ""
        self.request_args = dict()
        super(BasicHandler, self).__init__(application, request, **kwargs)

    def response(self, status, message, data=None):
        if not data:
            data = dict()
        return_request = dict(status=status, message=message, data=data)
        self.write(json.dumps(return_request))

    def get_request_args(self, necessary_list=None):
        request_context = json.loads(self.request.body)
        self.session_id = request_context.get("session_id")
        self.request_args = request_context.get("post_vars")

        if necessary_list:
            for args in necessary_list:
                if args not in self.request_args:
                    self.response(RESPONSE_STATUS_BAD_REQUEST, RESPONSE_MESSAGE_BAD_REQUEST)

        return self.request_args


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


