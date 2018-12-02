#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/3

Author: 

Description: 

"""

import time
import json
from decimal import Decimal
from tornado import gen

from handles.base import BasicHandler, CallbackHandler, executor
from handles.base import CALLBACK_RESPONSE_SUCCESS_CODE
from handles.wx_api import unifiedorder, wx_sign
from model.base import open_session
from model.schema import TransactionOrder, TransactionNonOrder, Account, User
from utiles.exception import ParameterInvalidException, PlException
from utiles import random_tool
from conf import config


class AccountHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            user_id = self.get_argument("user_id")

            with open_session() as session:
                user = session.query(User).filter(User.id == user_id).one()
                account = session.query(Account).filter(Account.id == user.account_id).one()

                data = dict()
                data["id"] = account.id
                data["user_id"] = user.id
                data["amount"] = account.amount.__str__()
                data["deposit"] = account.deposit.__str__()
                data["state"] = account.state
                data["description"] = account.description
                data["update_time"] = account.update_time.strftime("%Y-%m-%d %H:%M:%S")
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
            request_args = self.request_args(necessary_list=necessary_list)
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


class DepositHandler(BasicHandler):
    @gen.coroutine
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
                session.flush()

            if config.get("debug"):
                prepay_id = "wx201411101639507cbf6ffd8b0779950874"
            else:
                # 调用统一下单API
                unifiedorder_args = dict(
                    appid=config.get("appid"),
                    mch_id=config.get("mch_id"),
                    nonce_str=transaction_id,
                    body="deposit",
                    out_trade_no=transaction_id,
                    total_fee=request_args["amount"],
                    spbill_create_ip=self.request.remote_ip,
                    notify_url="https://{hostname}:{port}/api/user/account/actions/deposit/{transaction_id}".format(
                        hostname=config.get("https_domain_name"),
                        port=config.get("https_listen_port"),
                        transaction_id=transaction.id),
                    trade_type="JSAPI"
                )
                unifiedorder_ret = yield executor.submit(unifiedorder, args=unifiedorder_args)
                if unifiedorder_ret["return_code"] != CALLBACK_RESPONSE_SUCCESS_CODE:
                    raise PlException("调用微信统一下单接口失败:%s" % unifiedorder_ret["return_msg"])

                if unifiedorder_ret["result_code"] != CALLBACK_RESPONSE_SUCCESS_CODE:
                    raise PlException("调用微信统一下单接口出错 err_code:%s err_code_des:%s " % (
                        unifiedorder_ret["err_code"], unifiedorder_ret["err_code_des"]))

                prepay_id = unifiedorder_ret["prepay_id"]

            # 生成签名
            data = dict()
            data["appid"] = config.get("appid")
            data["timeStamp"] = str(int(time.time()))
            data["nonceStr"] = transaction_id
            data["package"] = "prepay_id=%s" % prepay_id
            data["signType"] = "MD5"
            data["paySign"] = wx_sign(data)
            data["id"] = transaction.id

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

                if request_args["return_code"] != CALLBACK_RESPONSE_SUCCESS_CODE:
                    transaction.wx_transaction_id = request_args["transaction_id"]
                    transaction.state = TransactionNonOrder.STATE_FAILED
                    transaction.description = "支付失败:%s" % request_args["return_msg"]
                    self.response()
                    return

                # 校验签名
                sign = request_args.pop("sign")
                if sign != wx_sign(request_args):
                    raise PlException("校验签名失败")

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


class RedemptionHandler(BasicHandler):
    def post(self):
        try:
            necessary_list = ["user_id"]
            request_args = self.request_args(necessary_list=necessary_list)

            user_id = request_args["user_id"]
            transaction_id = random_tool.random_string()

            with open_session() as session:
                account = session.query(Account).filter(Account.user_id == user_id).one()

                transaction = TransactionNonOrder(
                    user_id=request_args["user_id"],
                    transaction_id=transaction_id,
                    wx_transaction_id=TransactionNonOrder.WX_TRANSACTION_ID,
                    type=TransactionNonOrder.TYPE_RETURN_DEPOSIT,
                    state=TransactionNonOrder.STATE_UNFINISH,
                    amount=account.deposit,
                    description="等待退还押金"
                )
                session.add(transaction)
                session.flush()

            self.response()
        except ParameterInvalidException as e:
            self.response_request_error(e)
        except Exception as e:
            self.response_server_error(e)


class WithdrawHandler(BasicHandler):
    def post(self):
        try:
            necessary_list = ["user_id", "amount"]
            request_args = self.request_args(necessary_list=necessary_list)

            user_id = request_args["user_id"]
            amount = request_args["amount"]
            transaction_id = random_tool.random_string()

            with open_session() as session:
                account = session.query(Account).filter(Account.user_id == user_id).one()
                unfinish_orders = session.query(TransactionNonOrder).filter(
                    TransactionNonOrder.user_id == user_id,
                    TransactionNonOrder.state == TransactionNonOrder.STATE_UNFINISH,
                    TransactionNonOrder.type == TransactionNonOrder.TYPE_WITHDRAW_CASH).all()

                if unfinish_orders:
                    raise PlException("存在未完成的提现请求，请完成后再继续申请提现")

                if account.amount < amount:
                    raise PlException("余额不足，请确认金额是否正确")

                transaction = TransactionNonOrder(
                    user_id=request_args["user_id"],
                    transaction_id=transaction_id,
                    wx_transaction_id=TransactionNonOrder.WX_TRANSACTION_ID,
                    type=TransactionNonOrder.TYPE_WITHDRAW_CASH,
                    state=TransactionNonOrder.STATE_UNFINISH,
                    amount=amount,
                    description="等待提现到账"
                )
                session.add(transaction)
                session.flush()

            self.response()
        except ParameterInvalidException as e:
            self.response_request_error(e)
        except Exception as e:
            self.response_server_error(e)
