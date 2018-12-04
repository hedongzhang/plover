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
from model.schema import User, Account, Order, Message, Verification
from utiles.exception import ParameterInvalidException, PlException
from utiles import logger


class UserHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            user_id = self.get_argument("user_id")

            with open_session() as session:
                user = session.query(User).filter(User.id == user_id).one()
                account = session.query(Account).filter(Account.id == user.account_id).one()

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
                data["nick_name"] = user.nick_name
                data["first_name"] = user.first_name
                data["last_name"] = user.last_name
                data["phone"] = user.phone
                data["state"] = user.state
                data["undone_order_count"] = undone_order_count
                data["unread_message_count"] = unread_message_count
                data["amount"] = account.amount.__str__()

            self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)

    def post(self):
        try:
            necessary_list = ["user_id", "user_info", "raw_data", "signature", "encrypted_data", "iv"]
            request_args = self.request_args(necessary_list=necessary_list)
            user_info = json.loads(request_args["user_info"])

            with open_session() as session:
                user = session.query(User).filter(User.id == request_args["user_id"]).one()
                user.nick_name = user_info["nickName"]
                user.avatar_url = user_info["avatarUrl"]
                user.gender = user_info["gender"]

                user.description = "注册完成"

            self.response()
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)

    def put(self):
        try:
            necessary_list = ["user_id", "school", "first_name", "last_name", "phone", "verification_code", "gender",
                              "id_number", "id_photo_path"]
            request_args = self.request_args(necessary_list=necessary_list)

            with open_session() as session:
                verification = session.query(Verification).filter(
                    Verification.phone == request_args["phone"]).one_or_none()
                if not verification or verification.verification_code != request_args["verification_code"]:
                    raise PlException("验证码校验失败，请检查手机验证码")

                user = session.query(User).filter(User.id == request_args["user_id"]).one()
                for attr in necessary_list[1:]:
                    user.__setattr__(attr, request_args[attr])

                user.description = "已完善资料，等待缴纳押金"

            self.response()
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)


class UsersHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            state = self.get_argument("state")
            status = self.get_argument("status")

            limit = self.get_argument("limit")
            offset = self.get_argument("offset")
            if (limit == "") or (offset == ""):
                raise PlException("分页参数不能为空值")

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
                    user_info["nick_name"] = user.nick_name
                    user_info["first_name"] = user.first_name
                    user_info["last_name"] = user.last_name
                    user_info["state"] = user.state
                    user_info["phone"] = user.phone
                    data["user_list"].append(user_info)

            self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)
