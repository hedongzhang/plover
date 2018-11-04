#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/1

Author: 

Description: 

"""

from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Boolean, String, Float, DECIMAL

from model.base import Entity


class User(Entity):
    """
        用户表
    """
    __tablename__ = "user"

    GENDER_UNKNOWN = 0
    GENDER_MALE = 1
    GENDER_FEMALE = 2

    STATUS_UNLOGIN = 0
    STATUS_LOGIN = 1

    STATE_FREEZE = 0
    STATE_NOT_CERTIFICATION = 1
    STATE_CERTIFICATION = 2

    openid = Column(Integer, nullable=False, unique=True, doc="微信用户的openid")
    unionid = Column(Integer, nullable=False, unique=True, doc="微信用户的unionid")
    balance_id = Column(Integer, nullable=False, unique=True, doc="账户id, -1表示刚刚注册，在创建账户时中断")
    nick_name = Column(String(length=64), doc="昵称")
    avatar_url = Column(String(length=256), doc="头像URL")
    gender = Column(Integer, nullable=False, doc="性别: 0-未知, 1-男, 2-女")
    first_name = Column(String(length=64), doc="名")
    last_name = Column(String(length=64), doc="姓")
    phone = Column(String(length=16), doc="手机号")
    school = Column(String(length=256), doc="学校")
    id_number = Column(String(length=64), unique=True, doc="身份证号码")
    id_photo_path = Column(String(length=256), unique=True, doc="身份证图片路径")
    status = Column(Integer, nullable=False, doc="即时状态: 0-未登录，1-已经登录")
    state = Column(Integer, nullable=False, doc="状态: 0-冻结, 1-未认证，2-已认证")
    score = Column(Integer, nullable=False, doc="用户评分")

    description = Column(String(length=256), doc="备注")
    create_time = Column(DateTime, default=datetime.now, doc="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, doc="更新时间utc")


class Session(Entity):
    """
        会话表
    """
    __tablename__ = "session"

    user_id = Column(Integer, nullable=False, unique=True, doc="用户id")
    session_id = Column(String(length=128), nullable=False, doc="用户session_id")
    wx_session_key = Column(String(length=128), nullable=False, unique=True, doc="微信登录session")

    description = Column(String(length=256), doc="备注")
    create_time = Column(DateTime, default=datetime.now, doc="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, doc="更新时间utc")


class Message(Entity):
    """
        用户消息表
    """
    __tablename__ = "message"

    STATE_UNREAD = 0
    STATE_READED = 1

    TYPE_NORMAL = 0

    user_id = Column(Integer, nullable=False, doc="用户id")
    title = Column(String(length=64), doc="标题")
    context = Column(String(length=512), doc="内容")
    type = Column(Integer, nullable=False, default=0, doc="类型: 0-一般消息")
    state = Column(Integer, nullable=False, doc="状态: 0-未读, 1-已读")

    description = Column(String(length=256), doc="备注")
    create_time = Column(DateTime, default=datetime.now, doc="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, doc="更新时间utc")


class Address(Entity):
    """
        用户地址表
    """
    __tablename__ = "address"

    TYPE_TACK = 0
    TYPE_SEND = 1

    PROPERTY_FEMALE = 0
    PROPERTY_MALE = 1
    PROPERTY_PUBLIC = 2

    user_id = Column(Integer, nullable=False, doc="用户id")
    nick_name = Column(String(length=64), doc="昵称")
    type = Column(Integer, nullable=False, default=0, doc="类型: 0-取货地址, 1-收货地址")
    property = Column(Integer, nullable=False, doc="属性: 0-女性场所, 1-男性场所, 2-公共场所")
    first_name = Column(String(length=64), doc="名")
    last_name = Column(String(length=64), doc="姓")
    phone = Column(String(length=16), doc="手机号")
    first_address = Column(String(length=256), doc="大致地址")
    last_address = Column(String(length=256), doc="详细地址")
    latitude = Column(Float(32), nullable=False, doc="纬度")
    longitude = Column(Float(32), nullable=False, doc="经度")
    default = Column(Boolean, nullable=False, doc="是否为默认地址")

    description = Column(String(length=256), doc="备注")
    create_time = Column(DateTime, default=datetime.now, doc="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, doc="更新时间utc")


class Balance(Entity):
    """
        用户账户表
    """
    __tablename__ = "balance"

    STATE_FREEZE = 0
    STATE_NORMAL = 1

    user_id = Column(Integer, nullable=False, unique=True, doc="用户id")
    amount = Column(DECIMAL(10,2), nullable=False, doc="账户余额")
    deposit = Column(DECIMAL(10,2), nullable=False, doc="押金")
    state = Column(Integer, nullable=False, doc="状态: 0-冻结, 1-正常")

    description = Column(String(length=256), doc="备注")
    create_time = Column(DateTime, default=datetime.now, doc="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, doc="更新时间utc")


class Order(Entity):
    """
        订单表
    """
    __tablename__ = "order"

    STATE_UNPAID = 0
    STATE_NOORDER = 1
    STATE_ORDERS = 2
    STATE_DISTRIBUTION = 3
    STATE_ARRIVE = 4
    STATE_FINISH = 5
    STATE_CANCEL = 6

    master_id = Column(Integer, nullable=False, doc="雇主id")
    slave_id = Column(Integer, nullable=False, doc="佣兵id")
    takeaway_id = Column(Integer, nullable=False, doc="外卖id")
    amount = Column(DECIMAL(10,2), nullable=False, doc="订单金额")
    tip = Column(DECIMAL(10,2), nullable=False, doc="小费")
    verification_code = Column(String(length=64), nullable=False, doc="验证码")
    state = Column(Integer, nullable=False, doc="状态: 0-未支付，1-未接单，2-已接单，3-配送中，4-已送达, 5-完成, 6-已取消")
    order_time = Column(DateTime, default=datetime.now, doc="接单时间utc")
    distribution_time = Column(DateTime, default=datetime.now, doc="配送时间utc")
    finish_time = Column(DateTime, default=datetime.now, doc="完成时间utc")

    description = Column(String(length=256), doc="备注")
    create_time = Column(DateTime, default=datetime.now, doc="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, doc="更新时间utc")


class Takeaway(Entity):
    """
        订单外卖表
    """
    __tablename__ = "takeaway"

    STATE_NOT_ARRIVE = 0
    STATE_ARRIVE = 1

    name = Column(String(length=64), doc="名称")
    start_addr_id = Column(Integer, nullable=False, doc="起始地址id")
    end_addr_id = Column(Integer, nullable=False, doc="送达地址id")
    number = Column(Integer, nullable=False, doc="份数")
    state = Column(Integer, nullable=False, doc="状态: 0-未到中转站，1-已到中转站")
    distribution_time = Column(DateTime, default=datetime.now, doc="确认到达中转站时间utc")

    description = Column(String(length=256), doc="备注")
    create_time = Column(DateTime, default=datetime.now, doc="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, doc="更新时间utc")


class TransactionOrder(Entity):
    """
        订单交易表
    """
    __tablename__ = "transaction_order"

    TYPE_ORDERS = 0
    TYPE_COLLECT = 1
    TYPE_CANCEL = 2

    user_id = Column(Integer, nullable=False, doc="用户id")
    order_id = Column(Integer, nullable=False, doc="订单id")
    wx_transaction_id = Column(String(length=64), nullable=False, doc="订单id")
    type = Column(Integer, nullable=False, doc="0-雇主下单，1-佣兵收款，2-雇主取消订单")
    amount = Column(DECIMAL(10,2), nullable=False, doc="交易金额")
    commission = Column(DECIMAL(10,2), nullable=False, doc="平台佣金")

    description = Column(String(length=256), doc="备注")
    create_time = Column(DateTime, default=datetime.now, doc="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, doc="更新时间utc")


class TransactionNonOrder(Entity):
    """
        非订单交易表
    """
    __tablename__ = "transaction_non_order"

    TYPE_ADMIN = 0
    TYPE_PAY_DEPOSIT = 1
    TYPE_RETURN_DEPOSIT = 2
    TYPE_SAVE_CASH = 3
    TYPE_WITHDRAW_CASH = 4

    user_id = Column(Integer, nullable=False, doc="用户id")
    wx_transaction_id = Column(Integer, nullable=False, doc="订单id")
    type = Column(Integer, nullable=False, doc="0-管理员操作, 1-缴纳押金，2-退还押金，3-存入账户，4-从账户提现")
    amount = Column(DECIMAL(10,2), nullable=False, doc="交易金额")

    description = Column(String(length=256), doc="备注")
    create_time = Column(DateTime, default=datetime.now, doc="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, doc="更新时间utc")


class Config(Entity):
    """
        平台配置表
    """
    __tablename__ = "config"

    TYPE = 0

    key = Column(String(length=32), doc="配置名称")
    value = Column(String(length=32), doc="配置值")
    type = Column(String(length=32), doc="类型: 0-一般配置")

    description = Column(String(length=256), doc="备注")
    create_time = Column(DateTime, default=datetime.now, doc="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, doc="更新时间utc")


if __name__ == '__main__':
    from model.base import open_session

    with open_session() as session:
        users = session.query(User).all()
        for user in users:
            print(user.to_dict)
