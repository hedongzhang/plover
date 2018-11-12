#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/3

Author: 

Description: 

"""

import json

from handles.base import BasicHandler
from model.base import open_session
from model.schema import User, Balance, TransactionOrder, Message
from utiles import config
from utiles.exception import ParameterInvalidException


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
                data["amount"] = balance.amount.__str__()
                data["deposit"] = balance.deposit.__str__()
                data["state"] = balance.state
                data["description"] = balance.description
                data["update_time"] = balance.update_time.strftime("%Y-%m-%d %H:%M:%S")
                data["income"] = 0
                data["transaction_list"] = list()

                query = session.query(TransactionOrder).filter(TransactionOrder.user_id == user_id)
                query = query.order_by(TransactionOrder.create_time.desc()).limit(config.get("query_num"))
                transactions = query.all()

                for transaction in transactions:
                    if transaction.type == TransactionOrder.TYPE_COLLECT:
                        data["income"] += transaction.amount

                    transaction_info = dict()
                    transaction_info["id"] = transaction.id
                    transaction_info["order_id"] = transaction.order_id
                    transaction_info["wx_transaction_id"] = transaction.wx_transaction_id
                    transaction_info["type"] = transaction.type
                    transaction_info["amount"] = transaction.amount.__str__()
                    transaction_info["commission"] = transaction.commission.__str__()
                    transaction_info["description"] = transaction.description
                    transaction_info["create_time"] = transaction.create_time.strftime("%Y-%m-%d %H:%M:%S")

                    data["transaction_list"].append(transaction_info)
                data["income"] = data["income"].__str__()

            self.response(data)
        except ParameterInvalidException as e:
            self.response_request_error(e)
        except Exception as e:
            self.response_server_error(e)

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
        except ParameterInvalidException as e:
            self.response_request_error(e)
        except Exception as e:
            self.response_server_error(e)
