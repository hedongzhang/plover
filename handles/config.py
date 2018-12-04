#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/3

Author: 

Description: 

"""

from handles.base import BasicHandler
from model.base import open_session
from model.schema import Config
from utiles import logger


class ConfigHandler(BasicHandler):
    def get(self):
        data = dict()
        with open_session() as session:
            configs = session.query(Config).all()
            for config in configs:
                data[config.key] = config.value

        self.response(data=data)

    def post(self):
        try:
            request_args = self.request_args()

            with open_session() as session:
                for key, value in request_args.items():
                    config = Config(
                        key=key,
                        value=value,
                        type=Config.TYPE_NORMAL,
                    )
                    session.add(config)

            self.response()
        except Exception as e:
            logger.exception()
            self.response_server_error(e)
