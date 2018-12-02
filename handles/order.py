#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/12/2

Author: 

Description: 

"""

import time
from decimal import Decimal
from datetime import datetime

from tornado import gen
from sqlalchemy import or_

from conf import config
from handles.base import BasicHandler, CallbackHandler, executor
from handles.base import CALLBACK_RESPONSE_SUCCESS_CODE
from handles.wx_api import unifiedorder, wx_sign
from model.base import open_session
from model.schema import Config, Order, Takeaway, TransactionOrder, Address, User
from utiles.exception import ParameterInvalidException, PlException
from utiles.random_tool import random_string


class OrderHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            order_id = self.get_argument("order_id")

            with open_session() as session:
                order = session.query(Order).filter(Order.id == order_id).one_or_none()
                if not order:
                    raise PlException("此订单不存在")

                master_user = session.query(User).filter(User.id == order.master_id).one()
                slave_user = session.query(User).filter(User.id == order.slave_id).one_or_none()

                takeaway = session.query(Takeaway).filter(Takeaway.id == order.takeaway_id).one()
                tack_address = session.query(Address).filter(Address.id == takeaway.tack_address_id).one()
                recive_address = session.query(Address).filter(Address.id == takeaway.recive_address_id).one()

                data = dict()
                data["state"] = order.state
                data["amount"] = order.amount.__str__()
                data["tip"] = order.tip.__str__()
                data["verification_code"] = order.verification_code

                data["create_time"] = order.create_time.strftime("%Y-%m-%d %H:%M:%S")
                data["order_time"] = order.order_time.strftime("%Y-%m-%d %H:%M:%S")
                data["distribution_time"] = order.distribution_time.strftime("%Y-%m-%d %H:%M:%S")
                data["finish_time"] = order.finish_time.strftime("%Y-%m-%d %H:%M:%S")
                data["description"] = order.description

                data["master_info"] = dict(
                    user_id=master_user.id,
                    nick_name=master_user.nick_name
                )
                if slave_user:
                    data["slave_info"] = dict(
                        user_id=slave_user.id,
                        first_name=slave_user.first_name,
                        last_name=slave_user.last_name,
                        phone=slave_user.phone
                    )
                data["tack_address"] = dict(
                    first_address=tack_address.first_address,
                    last_address=tack_address.last_address,
                    shop_name=tack_address.shop_name
                )
                data["recive_address"] = dict(
                    first_address=recive_address.first_address,
                    last_address=recive_address.last_address,
                    phone=recive_address.phone
                )
                data["takeaway_info"] = dict(
                    id=takeaway.id,
                    state=takeaway.state
                )

                self.response(data)
        except ParameterInvalidException as e:
            self.response_request_error(e)
        except Exception as e:
            self.response_server_error(e)

    @gen.coroutine
    def post(self):
        try:
            necessary_list = ["master_id", "tack_address_id", "recive_address_id", "takeaway_state", "amount",
                              "description"]
            request_args = self.request_args(necessary_list=necessary_list)

            with open_session() as session:
                # 参数校验
                address = session.query(Address).filter(Address.id == request_args["tack_address_id"]).one_or_none()
                if not address:
                    raise ParameterInvalidException("取货地址不存在")
                address = session.query(Address).filter(Address.id == request_args["recive_address_id"]).one_or_none()
                if not address:
                    raise ParameterInvalidException("送货地址不存在")

                # 生成外卖数据
                takeaway = Takeaway(
                    tack_address_id=request_args["tack_address_id"],
                    recive_address_id=request_args["recive_address_id"],
                    state=request_args["takeaway_state"]
                )
                if takeaway.state == Takeaway.STATE_ARRIVE:
                    takeaway.distribution_time = datetime.now()
                session.add(takeaway)
                session.flush()

                # 生成订单数据
                order = Order(
                    master_id=request_args["master_id"],
                    takeaway_id=takeaway.id,
                    amount=request_args["amount"],
                    verification_code=random_string(4).lower(),
                    state=Order.STATE_UNPAID,
                    description=request_args["description"]
                )
                session.add(order)
                session.flush()

                # 生成交易数据
                transactionorder = TransactionOrder(
                    user_id=request_args["master_id"],
                    order_id=order.id,
                    transaction_id=random_string(),
                    wx_transaction_id=TransactionOrder.WX_TRANSACTION_ID,
                    type=TransactionOrder.TYPE_ORDERS,
                    amount=order.amount,
                    commission=0,
                    state=TransactionOrder.STATE_UNFINISH
                )
                session.add(transactionorder)

            # 调用微信支付API
            if config.get("debug"):
                prepay_id = random_string()
            else:
                # 调用统一下单API
                unifiedorder_args = dict(
                    appid=config.get("appid"),
                    mch_id=config.get("mch_id"),
                    nonce_str=transactionorder.transaction_id,
                    body="order",
                    out_trade_no=transactionorder.transaction_id,
                    total_fee=order.amount,
                    spbill_create_ip=self.request.remote_ip,
                    notify_url="https://{hostname}:{port}/api/order/{transaction_id}".format(
                        hostname=config.get("https_domain_name"),
                        port=config.get("https_listen_port"),
                        transaction_id=transactionorder.id),
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
            data["nonceStr"] = transactionorder.transaction_id
            data["package"] = "prepay_id=%s" % prepay_id
            data["signType"] = "MD5"
            data["paySign"] = wx_sign(data)
            data["id"] = order.id

            self.response(data)
        except ParameterInvalidException as e:
            self.response_request_error(e)
        except Exception as e:
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
            self.response_request_error(e)
        except Exception as e:
            self.response_server_error(e)


class OrdersHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            user_id = self.get_argument("user_id")
            state = self.get_argument("state")
            limit = self.get_argument("limit")
            offset = self.get_argument("offset")

            data = dict()

            with open_session() as session:
                query = session.query(Order)
                query = query.filter(or_(
                    Order.slave_id == user_id,
                    Order.master_id == user_id,
                ))

                if state:
                    query = query.filter(Order.state == state)

                data["count"] = query.count()
                query = query.limit(limit)
                query = query.offset(offset)

                data = list()
                for order in query.all():
                    takeaway = session.query(Takeaway).filter(Takeaway.id == order.takeaway_id).one()
                    tack_address = session.query(Address).filter(Address.id == takeaway.tack_address_id).one()
                    recive_address = session.query(Address).filter(Address.id == takeaway.recive_address_id).one()

                    order_info = dict()
                    order_info["id"] = order.id
                    order_info["state"] = order.state
                    order_info["amount"] = order.amount.__str__()
                    order_info["tip"] = order.tip.__str__()
                    order_info["master_id"] = order.master_id
                    order_info["slave_id"] = order.slave_id

                    order_info["create_time"] = order.create_time.strftime("%Y-%m-%d %H:%M:%S")
                    order_info["order_time"] = order.order_time.strftime("%Y-%m-%d %H:%M:%S")
                    order_info["distribution_time"] = order.distribution_time.strftime("%Y-%m-%d %H:%M:%S")
                    order_info["finish_time"] = order.finish_time.strftime("%Y-%m-%d %H:%M:%S")
                    order_info["description"] = order.description

                    order_info["tack_address"] = dict(
                        first_address=tack_address.first_address,
                        last_address=tack_address.last_address,
                        shop_name=tack_address.shop_name
                    )
                    order_info["recive_address"] = dict(
                        first_address=recive_address.first_address,
                        last_address=recive_address.last_address,
                        phone=recive_address.phone
                    )

                    data.append(order_info)

            self.response(data)
        except ParameterInvalidException as e:
            self.response_request_error(e)
        except Exception as e:
            self.response_server_error(e)


class CalculateHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            count = self.get_argument("count")

            with open_session() as session:
                amount_per_order = session.query(Config).filter(Config.key == "amount_per_order").one()
                amount = Decimal(amount_per_order.value) * Decimal(count)
                data = dict(amount=float(amount))

            self.response(data)
        except ParameterInvalidException as e:
            self.response_request_error(e)
        except Exception as e:
            self.response_server_error(e)


class OrderCallbackHandler(CallbackHandler):
    def post(self, transaction_id):
        try:
            necessary_list = ["return_code", "return_msg"]
            request_args = self.request_args(necessary_list=necessary_list)

            with open_session() as session:
                transaction = session.query(TransactionOrder).filter(
                    TransactionOrder.id == transaction_id).one_or_none()
                if not transaction:
                    raise PlException("无效的订单ID")

                if transaction.state == TransactionOrder.STATE_FINISH:
                    self.response()
                    return

                if request_args["return_code"] != CALLBACK_RESPONSE_SUCCESS_CODE:
                    transaction.wx_transaction_id = request_args["transaction_id"]
                    transaction.state = TransactionOrder.STATE_FAILED
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

                # 交易成功，更新交易状态
                transaction.wx_transaction_id = request_args["transaction_id"]
                transaction.state = TransactionOrder.STATE_FINISH
                transaction.description = "支付成功"
                # 更新订单状态
                order = session.query(Order).filter(Order.id == transaction.order_id).one()
                order.state = Order.STATE_NOORDER

            self.response()
        except ParameterInvalidException as e:
            self.response_error("参数格式校验错误:%s" % e)
        except Exception as e:
            self.response_error(e)
