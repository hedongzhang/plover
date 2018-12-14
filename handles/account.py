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
from model.schema import TransactionOrder, TransactionNonOrder, Account, User, Message
from utiles.exception import ParameterInvalidException, PlException
from utiles import random_tool, logger
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

                unfinish_withdraw_orders = session.query(TransactionNonOrder).filter(
                    TransactionNonOrder.user_id == user_id,
                    TransactionNonOrder.state == TransactionNonOrder.STATE_UNFINISH,
                    TransactionNonOrder.type == TransactionNonOrder.TYPE_WITHDRAW_CASH).all()
                unfinish_withdraw_amount = Decimal("0.00")
                for unfinish_withdraw_order in unfinish_withdraw_orders:
                    unfinish_withdraw_amount += unfinish_withdraw_order.amount
                data["withdraw_amount"] = (account.amount - unfinish_withdraw_amount).__str__()

                data["deposit"] = account.deposit.__str__()
                data["state"] = account.state
                data["description"] = account.description
                data["update_time"] = account.update_time.strftime("%Y-%m-%d %H:%M:%S")
                data["income"] = 0
                data["transaction_list"] = list()

                query = session.query(TransactionOrder).filter(TransactionOrder.user_id == user_id,
                                                               TransactionOrder.state == TransactionOrder.STATE_FINISH)
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
                    transaction_info["amount"] = (transaction.amount - transaction.commission).__str__()
                    transaction_info["slave_amount"] = (transaction.amount - transaction.commission).__str__()
                    if transaction.type == TransactionOrder.TYPE_COLLECT or transaction.type == TransactionOrder.TYPE_CANCEL:
                        transaction_info["is_income"] = True
                    else:
                        transaction_info["is_income"] = False
                    transaction_info["commission"] = transaction.commission.__str__()
                    transaction_info["description"] = transaction.description
                    transaction_info["create_time"] = transaction.create_time.strftime("%Y-%m-%d %H:%M:%S")
                    # gyp要求
                    if transaction_info["type"] in [TransactionOrder.TYPE_CANCEL, TransactionOrder.TYPE_ORDERS,
                                                    TransactionOrder.TYPE_COLLECT]:
                        data["transaction_list"].append(transaction_info)
                data["income"] = data["income"].__str__()

            self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)

    def post(self):
        pass


class DepositHandler(BasicHandler):
    @gen.coroutine
    def post(self):
        try:
            necessary_list = ["user_id", "amount"]
            request_args = self.request_args(necessary_list=necessary_list)

            with open_session() as session:
                user = session.query(User).filter(User.id == request_args["user_id"]).one_or_none()
                if not user:
                    raise ParameterInvalidException("用户不存在")

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
                callback_url = "https://{hostname}:{port}/api/user/account/actions/deposit/{transaction_id}".format(
                    hostname=config.get("https_domain_name"),
                    port=config.get("https_listen_port"),
                    transaction_id=transaction.id)

                total_fee = (Decimal(str(request_args["amount"])) * Decimal("100")).quantize(Decimal('0'))

                unifiedorder_args = dict(
                    appid=config.get("appid"),
                    mch_id=config.get("mch_id"),
                    nonce_str=transaction_id,
                    body="deposit",
                    out_trade_no=transaction_id,
                    total_fee=total_fee.__str__(),
                    spbill_create_ip=self.request.remote_ip,
                    notify_url=callback_url,
                    trade_type="JSAPI",
                    openid=user.openid

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
            data["appId"] = config.get("appid")
            data["timeStamp"] = str(int(time.time()))
            data["nonceStr"] = transaction_id
            data["package"] = "prepay_id=%s" % prepay_id
            data["signType"] = "MD5"
            data["paySign"] = wx_sign(data)
            data["id"] = transaction.id

            self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)


class DepositCallbackHandler(CallbackHandler):
    def post(self, transaction_id):
        try:
            necessary_list = ["return_code"]
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
                    transaction.description = "支付失败:%s" % request_args[
                        "return_msg"] if "return_msg" in request_args else ""
                    self.response()
                    return

                # 校验签名
                sign = request_args.pop("sign")
                if sign != wx_sign(request_args):
                    raise PlException("校验签名失败")

                # 验证交易金额
                if Decimal(request_args["total_fee"]) != Decimal(str(transaction["amount"])) * Decimal("100"):
                    raise PlException("支付金额不对应")

                # 交易成功
                transaction.wx_transaction_id = request_args["transaction_id"]
                transaction.state = TransactionNonOrder.STATE_FINISH
                transaction.description = "支付成功"
                # 更新账户
                account = session.query(Account).filter(Account.user_id == transaction.user_id).one()
                account.deposit += transaction.amount

            self.response()
        except ParameterInvalidException as e:
            logger.exception()
            self.response_error("参数格式校验错误:%s" % e)
        except Exception as e:
            logger.exception()
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
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)


class WithdrawHandler(BasicHandler):
    def post(self):
        try:
            necessary_list = ["user_id", "amount"]
            request_args = self.request_args(necessary_list=necessary_list)

            user_id = request_args["user_id"]
            amount = Decimal(str(request_args["amount"]))
            transaction_id = random_tool.random_string()

            with open_session() as session:
                account = session.query(Account).filter(Account.user_id == user_id).one()

                unfinish_withdraw_orders = session.query(TransactionNonOrder).filter(
                    TransactionNonOrder.user_id == user_id,
                    TransactionNonOrder.state == TransactionNonOrder.STATE_UNFINISH,
                    TransactionNonOrder.type == TransactionNonOrder.TYPE_WITHDRAW_CASH).all()
                unfinish_withdraw_amount = Decimal("0.00")
                for unfinish_withdraw_order in unfinish_withdraw_orders:
                    unfinish_withdraw_amount += unfinish_withdraw_order.amount

                if account.amount - unfinish_withdraw_amount < amount:
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

                # 生成消息
                message = Message(user_id=user_id, title="提现",
                                  context="提现请求已确认，等待到账",
                                  state=Message.STATE_UNREAD)
                session.add(message)

            self.response()
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)


class WithdrawCallbackHandler(CallbackHandler):
    def post(self, transaction_id):
        try:
            necessary_list = ["return_code"]
            # request_args = self.request_args(necessary_list=necessary_list)
            request_args = self.request_args()

            with open_session() as session:
                transaction = session.query(TransactionNonOrder).filter(
                    TransactionNonOrder.id == transaction_id).one_or_none()
                if not transaction:
                    raise PlException("无效的订单ID")

                if transaction.state == TransactionNonOrder.STATE_FINISH:
                    self.response()
                    return

                # if request_args["return_code"] != CALLBACK_RESPONSE_SUCCESS_CODE:
                #     transaction.wx_transaction_id = request_args["transaction_id"]
                #     transaction.state = TransactionNonOrder.STATE_FAILED
                #     transaction.description = "支付失败:%s" % request_args[
                #         "return_msg"] if "return_msg" in request_args else ""
                #     self.response()
                #     return

                # 校验签名
                # sign = request_args.pop("sign")
                # if sign != wx_sign(request_args):
                #     raise PlException("校验签名失败")

                # 验证交易金额
                # if Decimal(request_args["total_fee"]) != Decimal(str(transaction["amount"])) * Decimal("100"):
                #     raise PlException("支付金额不对应")

                # 交易成功
                transaction.wx_transaction_id = request_args["transaction_id"]
                transaction.state = TransactionNonOrder.STATE_FINISH
                transaction.description = "支付成功"
                # 更新账户
                account = session.query(Account).filter(Account.user_id == transaction.user_id).one()
                account.amount -= transaction.amount

                # 生成消息
                message = Message(user_id=transaction.user_id, title="提现已完成",
                                  context="提现已完成，金额%s元已打入指定账户，目前账号余额%s元！" % (
                                  transaction.amount.__str__(), account.amount.__str__()),
                                  state=Message.STATE_UNREAD)
                session.add(message)

            self.response()
        except ParameterInvalidException as e:
            logger.exception()
            self.response_error("参数格式校验错误:%s" % e)
        except Exception as e:
            logger.exception()
            self.response_error(e)
