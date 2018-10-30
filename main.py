#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/10/16

Author: 

Description: 

"""

import json

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import application
from utiles import config


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


class CopywritingHandler(tornado.web.RequestHandler):
    def get(self):
        data = dict(master_title="这次，不需要自己拿",
                    master_desc="即使再忙，也别太累",
                    master_banner="同学帮送，快速送达",
                    slave_title="这次，赚点零花钱",
                    slave_desc="空闲之余，也有所得")
        returm_data = dict(return_code=0, message="返回相关文案", data=data)
        self.write(returm_data)


def main():
    app = application.Application()
    ssl_options = dict(certfile=config.get("certfile"), keyfile=config.get("keyfile"))
    http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_options)
    http_server.listen(config.get("https_listen_port"))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
