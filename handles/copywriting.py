#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/3

Author: 

Description: 

"""

from handles.base import BasicHandler
from handles.base import RESPONSE_STATUS_SUCESS, RESPONSE_MESSAGE_SUCESS


class CopywritingHandler(BasicHandler):
    def get(self):
        data = dict(master_title="这次，不需要自己拿",
                    master_desc="即使再忙，也别太累",
                    master_banner="同学帮送，快速送达",
                    slave_title="这次，赚点零花钱",
                    slave_desc="空闲之余，也有所得")
        self.response(RESPONSE_STATUS_SUCESS, RESPONSE_MESSAGE_SUCESS, data=data)
