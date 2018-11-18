#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/10/16

Author: 

Description: 

"""

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import application
from conf import config


def main():
    app = application.Application()
    ssl_options = dict(certfile=config.get("certfile"), keyfile=config.get("keyfile"))
    http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_options, max_body_size=config.get("max_body_size"))
    http_server.listen(config.get("https_listen_port"))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
