#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/18

Author: 

Description: 

"""
import time
from decimal import Decimal

from handles.base import BasicHandler, CallbackHandler
from handles.base import CALLBACK_RESPONSE_SUCESS_CODE
from model.base import open_session
from model.schema import TransactionNonOrder, Account, User
from utiles.exception import ParameterInvalidException, PlException
from utiles import random_tool


class DepositHandler(BasicHandler):
    def post(self):
        try:
            necessary_list = ["user_id", "amount"]
            request_args = self.request_args(necessary_list=necessary_list)

            transaction_id = random_tool.random_string()

            with open_session() as session:
                transaction = TransactionNonOrder(
                    user_id=request_args["user_id"],
                    transaction_id=transaction_id,
                    wx_transaction_id=TransactionNonOrder.WX_TRANSACTION_ID,
                    type=TransactionNonOrder.TYPE_PAY_DEPOSIT,
                    state=TransactionNonOrder.STATE_UNFINISH,
                    amount=request_args["amount"],
                    description="等待微信支付押金"
                )
                session.add(transaction)

            # TODO:调用微信支付
            prepay_id = "wx2017033010242291fcfe0db70013231072"

            # TODO:生成签名
            paySign = "22D9B4E54AB1950F51E0649E8810ACD6"

            data = dict()
            data["id"] = transaction.id
            data["timeStamp"] = str(int(time.time()))
            data["nonceStr"] = transaction_id
            data["package"] = "prepay_id={prepay_id}".format(prepay_id=prepay_id)
            data["paySign"] = paySign
            data["signType"] = "MD5"

            self.response(data)
        except ParameterInvalidException as e:
            self.response_request_error(e)
        except Exception as e:
            self.response_server_error(e)


class DepositCallbackHandler(CallbackHandler):
    def post(self, transaction_id):
        try:
            necessary_list = ["return_code", "return_msg"]
            request_args = self.request_args(necessary_list=necessary_list)

            with open_session() as session:
                transaction = session.query(TransactionNonOrder).filter(
                    TransactionNonOrder.id == transaction_id).one_or_none()
                if not transaction:
                    raise PlException("无效的订单ID")

                if transaction.state == TransactionNonOrder.STATE_FINISH:
                    self.response()
                    return

                if request_args["return_code"] != CALLBACK_RESPONSE_SUCESS_CODE:
                    transaction.wx_transaction_id = request_args["transaction_id"]
                    transaction.state = TransactionNonOrder.STATE_FAILED
                    transaction.description = "支付失败:%s" % request_args["return_msg"]
                    self.response()
                    return

                # TODO:验证签名
                sign = request_args["sign"]
                if not sign:
                    raise PlException("签名失败")

                # 验证交易金额
                if Decimal(request_args["total_fee"]) != transaction["amount"]:
                    raise PlException("支付金额不对应")

                # 交易成功
                transaction.wx_transaction_id = request_args["transaction_id"]
                transaction.state = TransactionNonOrder.STATE_FINISH
                transaction.description = "支付成功"
                # 更新账户
                account = session.query(Account).filter(Account.user_id == transaction.user_id).one()
                account.deposit += transaction.amount
                # 更新用户状态
                user = session.query(User).filter(User.id == transaction.user_id).one()
                user.state += User.STATE_CERTIFICATION
                user.description = "已认证"

            self.response()
        except ParameterInvalidException as e:
            self.response_error("参数格式校验错误:%s" % e)
        except Exception as e:
            self.response_error(e)
