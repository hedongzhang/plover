#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/10/16

Author: hedong.zhang@woqutech.com

Description: 

"""
import json

import tornado
from tornado import web, httpserver, ioloop
from tornado.options import define, options

define("port", default=443, help="run on the given port", type=int)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hello ")

    def post(self):
        try:
            post_vars = self.get_argument("post_vars")
            request_args = json.loads(post_vars)
        except:
            post_vars = json.loads(self.request.body).get("post_vars")
            request_args = post_vars

        open_id = request_args.get("open_id", 0)
        name = request_args.get("name", "hdzhang")

        self.write(json.dumps(dict(ret_code=0, status="success", open_id=open_id, name=name)))


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/user", IndexHandler)])

    ssl_options = dict(certfile="./conf/server.crt", keyfile="./conf/server.key")
    http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_options)
    http_server.listen(options.port)

    tornado.ioloop.IOLoop.instance().start()
