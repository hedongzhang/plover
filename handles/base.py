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


RESPONSE_STATUS_SUCESS = 200
RESPONSE_MESSAGE_SUCESS = "OK--调用正常"

RESPONSE_STATUS_BAD_REQUEST = 400
RESPONSE_MESSAGE_BAD_REQUEST = "Bad Request--调用不合法,缺少参数或者参数格式不正确"

RESPONSE_STATUS_SERVER_ERROR = 500
RESPONSE_MESSAGE_SERVER_ERROR = "Internal Server Error--服务端错误:{error_message}"


class BasicHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(BasicHandler, self).__init__(application, request, **kwargs)

    def response(self, status, message, data=None):
        if not data:
            data = dict()
        return_request = dict(status=status, message=message, data=data)
        self.write(json.dumps(return_request))

    def get_request_args(self, necessary_list=None):
        request_context = json.loads(self.request.body)
        if necessary_list:
            for args in necessary_list:
                if args not in request_context:
                    self.response(RESPONSE_STATUS_BAD_REQUEST, RESPONSE_MESSAGE_BAD_REQUEST)

        return request_context


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


