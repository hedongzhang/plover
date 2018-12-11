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

    openid = Column(String(length=64), nullable=False, unique=True, comment="微信用户的openid")
    unionid = Column(String(length=64), comment="微信用户的unionid")
    account_id = Column(Integer, nullable=False, unique=True, comment="账户id, -1表示刚刚注册，在创建账户时中断")
    nick_name = Column(String(length=64), comment="昵称")
    avatar_url = Column(String(length=256), comment="头像URL")
    gender = Column(Integer, nullable=False, comment="性别: 0-未知, 1-男, 2-女")
    first_name = Column(String(length=64), comment="名")
    last_name = Column(String(length=64), comment="姓")
    phone = Column(String(length=16), comment="手机号")
    school = Column(String(length=256), comment="学校")
    id_number = Column(String(length=64), unique=True, comment="身份证号码")
    id_photo_path = Column(String(length=256), unique=True, comment="身份证图片路径")
    status = Column(Integer, nullable=False, comment="即时状态: 0-未登录，1-已经登录")
    state = Column(Integer, nullable=False, comment="状态: 0-冻结, 1-未认证，2-已认证")
    score = Column(Integer, nullable=False, comment="用户评分")

    description = Column(String(length=256), comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment="更新时间utc")


class Session(Entity):
    """
        会话表
    """
    __tablename__ = "session"

    user_id = Column(Integer, nullable=False, unique=True, comment="用户id")
    session_id = Column(String(length=128), nullable=False, comment="用户session_id")
    wx_session_key = Column(String(length=128), nullable=False, unique=True, comment="微信登录session")

    description = Column(String(length=256), comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment="更新时间utc")


class Message(Entity):
    """
        用户消息表
    """
    __tablename__ = "message"

    STATE_UNREAD = 0
    STATE_READED = 1

    TYPE_NORMAL = 0

    user_id = Column(Integer, nullable=False, comment="用户id")
    title = Column(String(length=64), comment="标题")
    context = Column(String(length=512), comment="内容")
    type = Column(Integer, nullable=False, default=0, comment="类型: 0-一般消息")
    state = Column(Integer, nullable=False, comment="状态: 0-未读, 1-已读")

    description = Column(String(length=256), comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment="更新时间utc")


class Address(Entity):
    """
        用户地址表
    """
    __tablename__ = "address"

    TYPE_TACK = 0
    TYPE_RECIVE = 1

    PROPERTY_FEMALE = 0
    PROPERTY_MALE = 1
    PROPERTY_LIBRARY = 2
    PROPERTY_TEACH_BUILDING = 3
    PROPERTY_OTHER = 4

    STATE_NORMAL = 1
    STATE_DELETE = 0

    user_id = Column(Integer, nullable=False, comment="用户id")
    shop_name = Column(String(length=64), comment="商家名称")
    type = Column(Integer, nullable=False, default=0, comment="类型: 0-取货地址, 1-收货地址")
    property = Column(Integer, nullable=False, comment="属性: 0-女生宿舍，1-男生宿舍，2-图书馆，3-教学楼，4-其他")
    state = Column(Integer, nullable=False, default=1, comment="属性: 0-已删除，1-正常")
    first_name = Column(String(length=64), comment="名")
    last_name = Column(String(length=64), comment="姓")
    phone = Column(String(length=16), comment="手机号")
    first_address = Column(String(length=256), comment="大致地址")
    last_address = Column(String(length=256), comment="详细地址")
    latitude = Column(Float(32), nullable=False, comment="纬度")
    longitude = Column(Float(32), nullable=False, comment="经度")
    default = Column(Boolean, nullable=False, comment="是否为默认地址")

    description = Column(String(length=256), comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment="更新时间utc")


class Account(Entity):
    """
        用户账户表
    """
    __tablename__ = "account"

    STATE_FREEZE = 0
    STATE_NORMAL = 1

    user_id = Column(Integer, nullable=False, unique=True, comment="用户id")
    amount = Column(DECIMAL(10, 2), nullable=False, comment="账户余额")
    deposit = Column(DECIMAL(10, 2), nullable=False, comment="押金")
    state = Column(Integer, nullable=False, comment="状态: 0-冻结, 1-正常")

    description = Column(String(length=256), comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment="更新时间utc")


class Verification(Entity):
    """
        ﻿验证数据表
    """
    __tablename__ = "verification"

    phone = Column(String(length=16), nullable=False, unique=True, comment="手机号")
    verification_code = Column(String(length=64), nullable=False, comment="验证码")
    count = Column(Integer, nullable=False, comment="获取次数")

    description = Column(String(length=256), comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment="更新时间utc")


class Suggestion(Entity):
    """
        用户账户表
    """
    __tablename__ = "suggestion"

    user_id = Column(Integer, nullable=False, comment="用户id")
    context = Column(String(length=1024), comment="内容")
    path = Column(String(length=256), comment="截图路径")
    contact = Column(String(length=32), comment="联系方式")

    description = Column(String(length=256), comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment="更新时间utc")


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

    master_id = Column(Integer, nullable=False, comment="雇主id")
    slave_id = Column(Integer, nullable=False, default=0, comment="佣兵id")
    takeaway_id = Column(Integer, nullable=False, comment="外卖id")
    amount = Column(DECIMAL(10, 2), nullable=False, comment="订单金额")
    tip = Column(DECIMAL(10, 2), nullable=False, default=0, comment="小费")
    verification_code = Column(String(length=64), nullable=False, comment="验证码")
    state = Column(Integer, nullable=False, comment="状态: 0-未支付，1-未接单，2-已接单，3-配送中，4-已送达, 5-完成, 6-已取消")
    order_time = Column(DateTime, default=datetime.now, comment="接单时间utc")
    distribution_time = Column(DateTime, default=datetime.now, comment="配送时间utc")
    finish_time = Column(DateTime, default=datetime.now, comment="完成时间utc")

    description = Column(String(length=256), comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment="更新时间utc")


class Takeaway(Entity):
    """
        订单外卖表
    """
    __tablename__ = "takeaway"

    STATE_NOT_ARRIVE = 0
    STATE_ARRIVE = 1

    name = Column(String(length=64), comment="名称")
    tack_address_id = Column(Integer, nullable=False, comment="起始地址id")
    recive_address_id = Column(Integer, nullable=False, comment="送达地址id")
    state = Column(Integer, nullable=False, comment="状态: 0-未到中转站，1-已到中转站")
    distribution_time = Column(DateTime, comment="确认到达中转站时间utc")

    description = Column(String(length=256), comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment="更新时间utc")


class TransactionOrder(Entity):
    """
        订单交易表
    """
    __tablename__ = "transaction_order"

    TYPE_ORDERS = 0
    TYPE_ADDTIP = 1
    TYPE_CANCEL = 2
    TYPE_COLLECT = 3

    WX_TRANSACTION_ID = 0

    STATE_UNFINISH = 0
    STATE_FINISH = 1
    STATE_FAILED = 2
    STATE_ABNORMAL = 3

    user_id = Column(Integer, nullable=False, comment="用户id")
    order_id = Column(Integer, nullable=False, comment="订单id")
    transaction_id = Column(String(length=128), nullable=False, comment="交易id")
    wx_transaction_id = Column(String(length=64), nullable=False, comment="微信交易id, 0-未实际发生微信交易")
    type = Column(Integer, nullable=False, comment="0-雇主下单, 1-雇主增加小费, 2-取消订单, 3-佣兵收款")
    state = Column(Integer, nullable=False, comment="交易状态，0-未完成，1-已完成, 2-交易失败, 3-交易异常")
    amount = Column(DECIMAL(10, 2), nullable=False, comment="交易金额")
    commission = Column(DECIMAL(10, 2), nullable=False, comment="平台佣金")

    description = Column(String(length=256), comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment="更新时间utc")


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

    WX_TRANSACTION_ID = 0

    STATE_UNFINISH = 0
    STATE_FINISH = 1
    STATE_FAILED = 2
    STATE_ABNORMAL = 3

    user_id = Column(Integer, nullable=False, comment="用户id")
    transaction_id = Column(String(length=128), nullable=False, comment="交易id")
    wx_transaction_id = Column(String(length=128), nullable=False, comment="微信交易id, 0-未实际发生微信交易")
    type = Column(Integer, nullable=False, comment="0-管理员操作, 1-缴纳押金，2-退还押金，3-存入账户，4-从账户提现")
    state = Column(Integer, nullable=False, comment="交易状态，0-未完成，1-已完成, 2-交易失败, 3-交易异常")
    amount = Column(DECIMAL(10, 2), nullable=False, comment="交易金额")

    description = Column(String(length=256), comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment="更新时间utc")


class Config(Entity):
    """
        平台配置表
    """
    __tablename__ = "config"

    TYPE_NORMAL = 0

    key = Column(String(length=32), comment="配置名称")
    value = Column(String(length=32), comment="配置值")
    type = Column(String(length=32), comment="类型: 0-一般配置")

    description = Column(String(length=256), comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment="更新时间utc")


class ADBanner(Entity):
    """
        广告配置表
    """
    __tablename__ = "adbanner"

    image_url = Column(String(length=32), comment="图片url")
    url = Column(String(length=32), comment="广告url")

    description = Column(String(length=256), comment="备注")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment="更新时间utc")


if __name__ == '__main__':
    from model.base import open_session

    with open_session() as session:
        users = session.query(User).all()
        for user in users:
            print(user.to_dict)
