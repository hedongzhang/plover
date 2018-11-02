#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/10/29

Author: 

Description: 

"""

import os
import yaml
import tornado.web

from utiles import logger


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "ui/template"),
            static_path=os.path.join(os.path.dirname(__file__), "ui/dist"),
        )
        handlers = self._load_handlers()
        super(Application, self).__init__(handlers, **settings)

    def _load_handlers(self):
        with open(os.path.join(os.path.dirname(__file__), "handles/handlers.yml")) as f:
            handler_conf = yaml.load(f)
            handlers = handler_conf['handlers']
            legal_handlers = list()

            for handler in handlers:
                url = handler['url']
                cls_path = handler['handler']
                opts = handler.get('opts', None)

                handler_cls = self._import_cls(cls_path)
                if not handler_cls:
                    logger.error("Failed to load handler:%s" % cls_path)
                    continue

                if not opts:
                    legal_handler = (url, handler_cls)
                else:
                    legal_handler = (url, handler_cls, opts)

                if legal_handler not in legal_handlers:
                    legal_handlers.append(legal_handler)

        return legal_handlers

    @staticmethod
    def _import_cls(cls_path):
        full_path = cls_path.split('.')
        if len(full_path) == 1:
            return None
        mod_path = '.'.join(full_path[:-1])
        cls_name = full_path[-1]
        try:
            module = __import__(mod_path, fromlist=[cls_name])
            return getattr(module, cls_name, None)
        except Exception as e:
            logger.exception("Import module: {nodule} error: {error}".format(nodule=mod_path, error=e))
            return None
