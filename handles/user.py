#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/10/30

Author: 

Description: 

"""

import json

from sqlalchemy import and_, or_

from handles.base import BasicHandler
from model.base import open_session
from model.schema import User, Balance, Order, Message


class UserHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            user_id = self.get_argument("user_id")

            with open_session() as session:
                user = session.query(User).filter(User.id == user_id).one()
                balance = session.query(Balance).filter(Balance.id == user.balance_id).one()

                undone_order_count = session.query(Order).filter(
                    and_(
                        or_(
                            Order.slave_id == user.id,
                            Order.master_id == user.id,
                        ),
                        Order.state != Order.STATE_FINISH,
                        Order.state != Order.STATE_CANCEL
                    )
                ).count()

                unread_message_count = session.query(Message).filter(Message.user_id == user.id,
                                                                     Message.state == Message.STATE_UNREAD).count()

                data = dict()
                data["id"] = user.id
                data["nick_name"] = user.nickname
                data["first_name"] = user.first_name
                data["last_name"] = user.last_name
                data["phone"] = user.phone
                data["state"] = user.state
                data["undone_order_count"] = undone_order_count
                data["unread_message_count"] = unread_message_count
                data["amount"] = balance.amount

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
                user.nickname = user_info["nickName"]
                user.avatar_url = user_info["avatarUrl"]
                user.gender = user_info["gender"]

                user.description = "注册完成"

            self.response()
        except Exception as e:
            self.response_error(e)


class UsersHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            state = self.get_argument("state")
            status = self.get_argument("status")
            limit = self.get_argument("limit")
            offset = self.get_argument("offset")

            data = dict()

            with open_session() as session:
                query = session.query(User)
                if state:
                    query = query.filter(User.state == state)
                if status:
                    query = query.filter(User.status == status)

                data["count"] = query.count()
                query = query.limit(limit)
                query = query.offset(offset)

                data["user_list"] = list()
                for user in query.all():
                    user_info = dict()
                    user_info["id"] = user.id
                    user_info["nick_name"] = user.nickname
                    user_info["first_name"] = user.first_name
                    user_info["last_name"] = user.last_name
                    user_info["state"] = user.state
                    user_info["phone"] = user.phone
                    data["user_list"].append(user_info)

            self.response(data)
        except Exception as e:
            self.response_error(e)
