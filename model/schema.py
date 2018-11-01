#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/1

Author: 

Description: 

"""

from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, text, String

from model.base import Entity


class PLUser(Entity):
    """
        ip 地址段
    """
    __tablename__ = "user"

    GENDER_FEMALE = 0
    GENDER_MALE = 1
    GENDER_UNKNOWN = 2

    STATUS_UNLOGIN = 0
    STATUS_LOGIN = 1

    STATE_FREEZE = 0
    STATE_NOT_CERTIFICATION = 1
    STATE_CERTIFICATION = 2

    open_id = Column(Integer, nullable=False, doc="微信用户的open_id")
    balance_id = Column(Integer, nullable=False, doc="账户id")
    nickname = Column(String(length=64), doc="昵称")
    avatar_url = Column(String(length=256), doc="头像URL")
    gender = Column(Integer, nullable=False, doc="性别: 0-女，1-男，2-未知")
    first_name = Column(String(length=64), doc="名")
    last_name = Column(String(length=64), doc="姓")
    phone = Column(String(length=16), doc="手机号")
    school = Column(String(length=256), doc="学校")
    id_number = Column(String(length=64), doc="身份证号码")
    id_photo_path = Column(String(length=256), doc="身份证图片路径")
    status = Column(Integer, nullable=False, doc="即时状态: 0-未登录，1-已经登录")
    state = Column(Integer, nullable=False, doc="状态: 0-冻结, 1-未认证，2-已认证")
    score = Column(Integer, nullable=False, doc="用户评分")

    description = Column(String(length=256), doc="备注")
    create_time = Column(DateTime, default=datetime.now, doc="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, doc="更新时间utc")


class PLSession(Entity):
    """
        ip
    """
    __tablename__ = "session"

    user_id = Column(Integer, nullable=False, doc="用户id")

    description = Column(String(length=256), doc="备注")
    create_time = Column(DateTime, default=datetime.now, doc="创建时间utc")
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, doc="更新时间utc")



if __name__ == '__main__':
    from model.base import open_session

    with open_session() as session:
        users = session.query(PLUser).all()
        for user in users:
            print(user.to_dict)
