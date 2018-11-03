#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/3

Author: 

Description: 

"""

import json

from sqlalchemy import and_, or_

from handles.base import BasicHandler
from model.base import open_session
from model.schema import User, Balance, Order, Message


class BalanceHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            user_id = self.get_argument("user_id")

            with open_session() as session:
                user = session.query(User).filter(User.id == user_id).one()
                balance = session.query(Balance).filter(Balance.id == user.balance_id).one()

                data = dict()
                data["id"] = balance.id
                data["user_id"] = user.id
                data["amount"] = balance.amount
                data["deposit"] = balance.deposit
                data["state"] = balance.state
                data["description"] = balance.description
                data["update_time"] = balance.update_time.strftime("%Y-%m-%d %H:%M:%S")
                # data["income"] =
                # data["transaction_list"] =

            self.response(data)
        except Exception as e:
            self.response_error(e)

    def post(self):
        try:
            necessary_list = ["user_id", "user_info", "raw_data", "signature", "encrypted_data", "iv"]
            request_args = self.post_request_args(necessary_list=necessary_list)
            user_info = json.loads(request_args["user_info"])

            with open_session() as session:
                user = session.query(User).filter(User.id == request_args["user_id"]).one()
                user.nick_name = user_info["nick_name"]
                user.avatar_url = user_info["avatarUrl"]
                user.gender = user_info["gender"]

                user.description = "注册完成"

            self.response()
        except Exception as e:
            self.response_error(e)
