#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/10/30

Author: 

Description: 

"""

import json

from handles.base import BasicHandler


class UserHandler(BasicHandler):
    def get(self):
        session_id = self.get_argument("session_id")
        user_id = self.get_argument("user_id")
        self.write(json.dumps(dict(session_id=session_id, user_id=user_id)))

    def post(self):
        try:
            request_context = self.get_request_args(["session_id", "post_vars"])
            session_id = request_context.get("session_id")
            post_vars = request_context.get("post_vars")

            result = dict()
            result["status"] = 200
            result["message"] = "注册用户成功!"
            result["date"] = dict()
            self.write(json.dumps(result))
        except Exception as e:
            result = dict()
            result["status"] = 400
            result["message"] = "参数错误!"
            result["date"] = dict()
            self.write(json.dumps(result))
