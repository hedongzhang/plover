#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/10/29

Author: 

Description: 

"""

import tornado.web

from utiles import config


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class StaticHandler(tornado.web.StaticFileHandler):
    def __init__(self, application, request, **kwargs):
        kwargs['path'] = config.get("static_path")
        super(StaticHanler, self).__init__(application, request, **kwargs)

    def data_received(self, chunk):
        pass
