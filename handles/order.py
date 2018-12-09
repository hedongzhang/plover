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
from model.schema import Config, Order, Takeaway, TransactionOrder, Address, User, Account, Verification
from utiles.exception import ParameterInvalidException, PlException
from utiles.random_tool import random_string, random_digits
import utiles.sms_xa as sms
from utiles import logger

# 存放所有未接单订单位置信息，用来加速推荐订单
UNORDERS = dict()


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
                data["total_amount"] = (order.tip + order.amount).__str__()
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
                    first_name=recive_address.first_name,
                    last_name=recive_address.last_name,
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
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
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
                user = session.query(User).filter(User.id == request_args["master_id"]).one_or_none()
                if not user:
                    raise ParameterInvalidException("用户不存在")

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
                    verification_code=random_digits(4),
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
                callback_url = "https://{hostname}:{port}/api/order/{transaction_id}".format(
                    hostname=config.get("https_domain_name"),
                    port=config.get("https_listen_port"),
                    transaction_id=transactionorder.id)
                total_fee = (Decimal(str(order.amount)) * Decimal("100")).quantize(Decimal('0'))

                unifiedorder_args = dict(
                    appid=config.get("appid"),
                    mch_id=config.get("mch_id"),
                    nonce_str=transactionorder.transaction_id,
                    body="order",
                    out_trade_no=transactionorder.transaction_id,
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
            data["nonceStr"] = transactionorder.transaction_id
            data["package"] = "prepay_id=%s" % prepay_id
            data["signType"] = "MD5"
            data["paySign"] = wx_sign(data)
            data["id"] = order.id

            self.response(data)
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


class OrdersHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            master_id = self.get_argument("master_id")
            slave_id = self.get_argument("slave_id")
            state = self.get_argument("state")

            limit = self.get_argument("limit")
            offset = self.get_argument("offset")
            if (limit == "") or (offset == ""):
                raise PlException("分页参数不能为空值")

            data = dict()

            with open_session() as session:
                query = session.query(Order)

                if not master_id and not slave_id:
                    raise PlException("master_id和slave_id必须传一个")
                if master_id:
                    query = query.filter(Order.master_id == master_id)
                if slave_id:
                    query = query.filter(Order.slave_id == slave_id)
                if state:
                    query = query.filter(Order.state == state)

                # 前端要求不显示未支付的订单
                query = query.filter(Order.state != Order.STATE_UNPAID)
                # 按时间倒序
                query = query.order_by(Order.create_time.desc())

                data["count"] = query.count()
                query = query.limit(limit)
                query = query.offset(offset)

                data["order_list"] = list()
                for order in query.all():
                    takeaway = session.query(Takeaway).filter(Takeaway.id == order.takeaway_id).one()
                    tack_address = session.query(Address).filter(Address.id == takeaway.tack_address_id).one()
                    recive_address = session.query(Address).filter(Address.id == takeaway.recive_address_id).one()

                    order_info = dict()
                    order_info["id"] = order.id
                    order_info["state"] = order.state
                    order_info["amount"] = order.amount.__str__()
                    order_info["tip"] = order.tip.__str__()
                    order_info["total_amount"] = (order.tip + order.amount).__str__()
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

                    data["order_list"].append(order_info)

            self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
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
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)


class SuggestHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            user_id = self.get_argument("user_id")
            longitude = self.get_argument("longitude")
            latitude = self.get_argument("latitude")

            limit = int(self.get_argument("limit"))
            offset = int(self.get_argument("offset"))
            if (limit == "") or (offset == ""):
                raise PlException("分页参数不能为空值")

            data = dict()

            unorders = dict()
            with open_session() as session:
                user = session.query(User).filter(User.id == user_id).one_or_none()
                if not user:
                    raise PlException("此用户不存在")

                orders = session.query(Order).filter(Order.state == Order.STATE_NOORDER).all()
                for order in orders:
                    takeaway = session.query(Takeaway).filter(Takeaway.id == order.takeaway_id).one()
                    address = session.query(Address).filter(Address.id == takeaway.recive_address_id).one()

                    if user.gender == User.GENDER_MALE and address.property != Address.PROPERTY_FEMALE:
                        unorders[order.id] = (address.latitude, address.longitude)
                    elif user.gender == User.GENDER_FEMALE and address.property != Address.PROPERTY_MALE:
                        unorders[order.id] = (address.latitude, address.longitude)

            data["count"] = len(unorders)
            data["order_list"] = list()

            if latitude and longitude:
                temp_orders = {k: ((float(longitude) - v[0]) ** 2) + ((float(latitude) - v[1]) ** 2) for k, v in
                               unorders.items()}
                sort_orders = sorted(temp_orders.items(), key=lambda x: x[1])
                sort_orders = sort_orders[offset:offset + limit]
            else:
                sort_orders = [(k, v) for k, v in unorders.items()]

            with open_session() as session:
                for sort_order in sort_orders:
                    order = session.query(Order).filter(Order.id == sort_order[0]).one_or_none()
                    if order:
                        order_info = dict()
                        order_info["id"] = order.id
                        order_info["state"] = order.state
                        order_info["amount"] = order.amount.__str__()
                        order_info["tip"] = order.tip.__str__()
                        order_info["total_amount"] = (order.tip + order.amount).__str__()
                        order_info["master_id"] = order.master_id
                        order_info["slave_id"] = order.slave_id

                        order_info["create_time"] = order.create_time.strftime("%Y-%m-%d %H:%M:%S")
                        order_info["order_time"] = order.order_time.strftime("%Y-%m-%d %H:%M:%S")
                        order_info["distribution_time"] = order.distribution_time.strftime("%Y-%m-%d %H:%M:%S")
                        order_info["finish_time"] = order.finish_time.strftime("%Y-%m-%d %H:%M:%S")
                        order_info["description"] = order.description

                        takeaway = session.query(Takeaway).filter(Takeaway.id == order.takeaway_id).one()
                        tack_address = session.query(Address).filter(Address.id == takeaway.tack_address_id).one()
                        recive_address = session.query(Address).filter(Address.id == takeaway.recive_address_id).one()

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

                        data["order_list"].append(order_info)

            self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)


class AddtipHandler(BasicHandler):
    @gen.coroutine
    def post(self):
        try:
            necessary_list = ["order_id", "amount"]
            request_args = self.request_args(necessary_list=necessary_list)

            with open_session() as session:
                # 参数校验
                order = session.query(Order).filter(Order.id == request_args["order_id"]).one_or_none()
                if not order:
                    raise ParameterInvalidException("此订单不存在")
                if order.state not in [Order.STATE_NOORDER, Order.STATE_ORDERS, Order.STATE_DISTRIBUTION]:
                    raise PlException("此订单状态无法增加小费")
                user = session.query(User).filter(User.id == order.master_id).one_or_none()
                if not user:
                    raise ParameterInvalidException("用户不存在")

                # 生成交易数据
                transactionorder = TransactionOrder(
                    order_id=order.id,
                    user_id=order.master_id,
                    transaction_id=random_string(),
                    wx_transaction_id=TransactionOrder.WX_TRANSACTION_ID,
                    type=TransactionOrder.TYPE_ADDTIP,
                    amount=Decimal(request_args["amount"]),
                    commission=0,
                    state=TransactionOrder.STATE_UNFINISH,
                    description="待支付"
                )
                session.add(transactionorder)
                session.flush()

            # 调用微信支付API
            if config.get("debug"):
                prepay_id = random_string()
            else:
                # 调用统一下单API
                callback_url = "https://{hostname}:{port}/api/order/actions/addtip/{transaction_id}".format(
                    hostname=config.get("https_domain_name"),
                    port=config.get("https_listen_port"),
                    transaction_id=transactionorder.id)

                total_fee = (Decimal(str(request_args["amount"])) * Decimal("100")).quantize(Decimal('0'))

                unifiedorder_args = dict(
                    appid=config.get("appid"),
                    mch_id=config.get("mch_id"),
                    nonce_str=transactionorder.transaction_id,
                    body="add tip",
                    out_trade_no=transactionorder.transaction_id,
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
            data["nonceStr"] = transactionorder.transaction_id
            data["package"] = "prepay_id=%s" % prepay_id
            data["signType"] = "MD5"
            data["paySign"] = wx_sign(data)
            data["id"] = transactionorder.id

            self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)


class CancleHandler(BasicHandler):
    def post(self):
        try:
            necessary_list = ["user_id", "order_id"]
            request_args = self.request_args(necessary_list=necessary_list)
            user_id = request_args["user_id"]
            order_id = request_args["order_id"]

            with open_session() as session:
                # 参数校验
                user = session.query(User).filter(User.id == user_id).one_or_none()
                if not user:
                    raise PlException("此用户不存在")
                order = session.query(Order).filter(Order.id == order_id).one_or_none()
                if not order:
                    raise ParameterInvalidException("此订单不存在")

                if user_id == order.master_id:
                    if order.state >= Order.STATE_DISTRIBUTION:
                        raise ParameterInvalidException("雇主无法取消此订单")
                elif order.slave_id and user_id == order.slave_id:
                    if order.state != Order.STATE_ORDERS:
                        raise ParameterInvalidException("佣兵无法取消此订单")
                else:
                    raise PlException("无效的用户id")

                # 取消订单
                order.state = Order.STATE_CANCEL
                if "description" in request_args:
                    order.description = request_args["description"]
                # 订单金额和小费退至个人账户
                account = session.query(Account).filter(Account.id == user.account_id).one()
                account.amount += order.amount + order.tip

                # 生成交易数据
                transactionorder = TransactionOrder(
                    order_id=order_id,
                    user_id=user_id,
                    transaction_id=random_string(),
                    wx_transaction_id=TransactionOrder.WX_TRANSACTION_ID,
                    type=TransactionOrder.TYPE_CANCEL,
                    amount=order.amount + order.tip,
                    commission=0,
                    state=TransactionOrder.STATE_FINISH,
                    description="订单已取消，退款至个人账户"
                )
                session.add(transactionorder)

                # UNORDERS.pop(order.id)

            self.response()
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)


class AcceptHandler(BasicHandler):
    def post(self):
        try:
            necessary_list = ["user_id", "order_id"]
            request_args = self.request_args(necessary_list=necessary_list)
            user_id = request_args["user_id"]
            order_id = request_args["order_id"]

            with open_session() as session:
                # 参数校验
                user = session.query(User).filter(User.id == user_id).one_or_none()
                if not user:
                    raise PlException("此用户不存在")
                order = session.query(Order).filter(Order.id == order_id).one_or_none()
                if not order:
                    raise ParameterInvalidException("此订单不存在")

                if user.state != User.STATE_CERTIFICATION:
                    raise ParameterInvalidException("用户账户未认证或已冻结，无法接单")
                if user_id == order.master_id:
                    raise ParameterInvalidException("雇主无法接自己发的订单")

                # 接单
                order.slave_id = user_id
                order.state = Order.STATE_ORDERS
                order.order_time = datetime.now()
                takeaway = session.query(Takeaway).filter(Takeaway.id == order.takeaway_id).one()
                if takeaway.state == Takeaway.STATE_ARRIVE:
                    order.state = Order.STATE_DISTRIBUTION
                    order.distribution_time = datetime.now()

                # UNORDERS.pop(order.id)

            self.response()
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)


class ArriveHandler(BasicHandler):
    def post(self):
        try:
            necessary_list = ["user_id", "order_id"]
            request_args = self.request_args(necessary_list=necessary_list)
            user_id = request_args["user_id"]
            order_id = request_args["order_id"]

            with open_session() as session:
                # 参数校验
                user = session.query(User).filter(User.id == user_id).one_or_none()
                if not user:
                    raise PlException("此用户不存在")
                order = session.query(Order).filter(Order.id == order_id).one_or_none()
                if not order:
                    raise ParameterInvalidException("此订单不存在")

                if user_id != order.master_id:
                    raise PlException("用户无法操作不属于自己的订单")

                # 到达
                takeaway = session.query(Takeaway).filter(Takeaway.id == order.takeaway_id).one()
                takeaway.state = Takeaway.STATE_ARRIVE

                if order.state == Order.STATE_ORDERS:
                    order.state = Order.STATE_DISTRIBUTION
                    order.distribution_time = datetime.now()

                    # 调用短信接口，发送短信通知
                    try:
                        user = session.query(User).filter(User.id == order.slave_id).one()
                        sms.send_message(self.session_id, user.phone, "您的订单已到达取货点，请及时领取！")
                    except Exception as e:
                        logger.warn("send sms failed! :%s" % e)

            self.response()
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)


class FinishHandler(BasicHandler):
    def post(self):
        try:
            necessary_list = ["user_id", "order_id", "verification_code"]
            request_args = self.request_args(necessary_list=necessary_list)
            user_id = request_args["user_id"]
            order_id = request_args["order_id"]
            verification_code = request_args["verification_code"]

            with open_session() as session:
                # 参数校验
                user = session.query(User).filter(User.id == user_id).one_or_none()
                if not user:
                    raise PlException("此用户不存在")
                order = session.query(Order).filter(Order.id == order_id).one_or_none()
                if not order:
                    raise ParameterInvalidException("此订单不存在")
                if user_id != order.slave_id:
                    raise PlException("不是此订单佣兵，无法确认订单")
                if order.state != Order.STATE_DISTRIBUTION:
                    raise PlException("此订单状态，无法确认订单")
                if verification_code != order.verification_code:
                    raise PlException("验证码校验失败，无法确认订单")

                # 完成订单
                order.state = Order.STATE_FINISH
                order.finish_time = datetime.now()
                # 计算平台佣金
                amount = order.amount + order.tip
                draw_cratio = session.query(Config).filter(Config.key == "draw_cratio").one()
                commission = (amount * Decimal(str(draw_cratio.value))).quantize(Decimal('0.00'))
                # 订单金额和小费划入佣兵账户
                account = session.query(Account).filter(Account.id == user.account_id).one()
                account.amount += amount - commission

                # 生成交易数据
                transactionorder = TransactionOrder(
                    order_id=order_id,
                    user_id=user_id,
                    transaction_id=random_string(),
                    wx_transaction_id=TransactionOrder.WX_TRANSACTION_ID,
                    type=TransactionOrder.TYPE_COLLECT,
                    amount=order.amount + order.tip,
                    commission=commission,
                    state=TransactionOrder.STATE_FINISH,
                    description="订单已完成"
                )
                session.add(transactionorder)

            self.response()
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)


class OrderCallbackHandler(CallbackHandler):
    def post(self, transaction_id):
        try:
            necessary_list = ["return_code"]
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

                # 交易成功，更新交易状态
                transaction.wx_transaction_id = request_args["transaction_id"]
                transaction.state = TransactionOrder.STATE_FINISH
                transaction.description = "支付成功"
                # 更新订单状态
                order = session.query(Order).filter(Order.id == transaction.order_id).one()
                order.state = Order.STATE_NOORDER
                # 加入待接单列表
                takeaway = session.query(Takeaway).filter(Takeaway.id == order.takeaway_id).one()
                tack_address = session.query(Address).filter(Address.id == takeaway.tack_address_id).one()
                # UNORDERS[order.id] = (tack_address.latitude, tack_address.longitude)

            self.response()
        except ParameterInvalidException as e:
            logger.exception()
            self.response_error("参数格式校验错误:%s" % e)
        except Exception as e:
            logger.exception()
            self.response_error(e)


class AddtipCallbackHandler(CallbackHandler):
    def post(self, transaction_id):
        try:
            necessary_list = ["return_code"]
            request_args = self.request_args(necessary_list=necessary_list)

            with open_session() as session:
                transaction = session.query(TransactionOrder).filter(
                    TransactionOrder.id == transaction_id).one_or_none()
                if not transaction:
                    raise PlException("查询不到此订单ID")

                if transaction.type != TransactionOrder.TYPE_ADDTIP:
                    raise PlException("无效的订单ID")

                if transaction.state == TransactionOrder.STATE_FINISH:
                    self.response()
                    return

                if request_args["return_code"] != CALLBACK_RESPONSE_SUCCESS_CODE:
                    transaction.wx_transaction_id = request_args["transaction_id"]
                    transaction.state = TransactionOrder.STATE_FAILED
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

                # 交易成功，更新交易状态
                transaction.wx_transaction_id = request_args["transaction_id"]
                transaction.state = TransactionOrder.STATE_FINISH
                transaction.description = "支付成功"
                # 更新订单状态
                order = session.query(Order).filter(Order.id == transaction.order_id).one()
                order.tip += transaction["amount"]

            self.response()
        except ParameterInvalidException as e:
            logger.exception()
            self.response_error("参数格式校验错误:%s" % e)
        except Exception as e:
            logger.exception()
            self.response_error(e)
