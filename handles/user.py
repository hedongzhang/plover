#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/10/30

Author: 

Description: 

"""

import json

from handles.base import BasicHandler
from model.base import open_session
from model.schema import User


class UserHandler(BasicHandler):
    def get(self):
        session_id = self.get_argument("session_id")
        user_id = self.get_argument("user_id")
        self.write(json.dumps(dict(session_id=session_id, user_id=user_id)))

    def post(self):
        try:
            necessary_list = ["user_id", "user_info", "raw_data", "signature", "encrypted_data", "iv"]
            request_args = self.get_request_args(necessary_list=necessary_list)
            user_info = json.loads(request_args["user_info"])

            with open_session() as session:
                user = session.query(User).filter(User.id == request_args["user_id"]).one()
                user.nickname = user_info["nickName"]
                user.avatar_url = user_info["avatarUrl"]
                user.gender = user_info["gender"]

                user.description = "注册完成"

            self.response()
        except Exception as e:
            self.response_error(e)
