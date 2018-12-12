#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/12/9

Author: 

Description: 

"""

from handles.base import BasicHandler
from model.base import open_session
from model.schema import TransactionOrder, TransactionNonOrder
from utiles.exception import ParameterInvalidException, PlException
from utiles import logger


class TransactionsHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            user_id = self.get_argument("user_id")
            type = self.get_argument("type")

            limit = self.get_argument("limit")
            offset = self.get_argument("offset")
            if (limit == "") or (offset == ""):
                raise PlException("分页参数不能为空值")

            data = dict()
            data["transaction_order"] = list()
            data["transaction_non_order"] = list()

            with open_session() as session:
                query = session.query(TransactionOrder).filter(TransactionOrder.user_id == user_id)
                if type:
                    query = query.filter(TransactionOrder.type == type)
                query = query.order_by(TransactionOrder.create_time.desc()).limit(limit)
                transactions = query.all()

                for transaction in transactions:
                    transaction_info = dict()
                    transaction_info["id"] = transaction.id
                    transaction_info["order_id"] = transaction.order_id
                    transaction_info["wx_transaction_id"] = transaction.wx_transaction_id
                    transaction_info["type"] = transaction.type
                    transaction_info["amount"] = (transaction.amount - transaction.commission).__str__()
                    transaction_info["slave_amount"] = (transaction.amount - transaction.commission).__str__()
                    if transaction.type == TransactionOrder.TYPE_COLLECT or transaction.type == TransactionOrder.TYPE_CANCEL:
                        transaction_info["is_income"] = True
                    else:
                        transaction_info["is_income"] = False
                    transaction_info["state"] = transaction.state
                    transaction_info["commission"] = transaction.commission.__str__()
                    transaction_info["description"] = transaction.description
                    transaction_info["create_time"] = transaction.create_time.strftime("%Y-%m-%d %H:%M:%S")

                    data["transaction_order"].append(transaction_info)

            with open_session() as session:
                query = session.query(TransactionNonOrder).filter(TransactionNonOrder.user_id == user_id)
                if type:
                    query = query.filter(TransactionNonOrder.type == type)
                query = query.order_by(TransactionNonOrder.create_time.desc()).limit(limit)
                transactions = query.all()

                for transaction in transactions:
                    transaction_info = dict()
                    transaction_info["id"] = transaction.id
                    transaction_info["wx_transaction_id"] = transaction.wx_transaction_id
                    transaction_info["type"] = transaction.type
                    transaction_info["amount"] = transaction.amount.__str__()
                    if transaction.type == TransactionNonOrder.TYPE_PAY_DEPOSIT or transaction.type == TransactionNonOrder.TYPE_SAVE_CASH:
                        transaction_info["is_income"] = True
                    else:
                        transaction_info["is_income"] = False
                    transaction_info["state"] = transaction.state
                    transaction_info["description"] = transaction.description
                    transaction_info["create_time"] = transaction.create_time.strftime("%Y-%m-%d %H:%M:%S")

                    data["transaction_non_order"].append(transaction_info)

            self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)
