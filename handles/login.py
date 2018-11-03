#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/3

Author: 

Description: 

"""

import random
import string

from tornado import gen

from handles.base import executor, BasicHandler
from handles.base import RESPONSE_STATUS_SERVER_ERROR, RESPONSE_MESSAGE_SERVER_ERROR, RESPONSE_STATUS_SUCESS, \
    RESPONSE_MESSAGE_SUCESS
from utiles import config, httpclient
from model.base import open_session
from model.schema import User, Balance, Session


class LoginHandler(BasicHandler):
    @gen.coroutine
    def post(self):
        try:
            request_context = self.get_request_args(necessary_list=["secret", "js_code", "appid"])
            code2session_request = dict()
            code2session_request["appid"] = request_context["appid"]
            code2session_request["secret"] = request_context["secret"]
            code2session_request["js_code"] = request_context["js_code"]
            code2session_request["grant_type"] = "authorization_code"

            code2session_response = yield executor.submit(httpclient.get, url=config.get("code2session_url"),
                                                          args=code2session_request)
            if code2session_response["errcode"] == 0:
                self.user_login(code2session_response)
            else:
                self.response(RESPONSE_STATUS_SERVER_ERROR,
                              RESPONSE_MESSAGE_SERVER_ERROR.format(
                                  error_message="微信API服务访问失败({errcode}:{errmsg})".format(**code2session_response)))

        except Exception as e:
            self.response(RESPONSE_STATUS_SERVER_ERROR,
                          RESPONSE_MESSAGE_SERVER_ERROR.format(error_message=e))

    def user_login(self, code2session_response):
        data = dict()

        openid = code2session_response["openid"]
        session_key = code2session_response["session_key"]
        unionid = code2session_response["unionid"]

        with open_session() as session:
            user = session.query(User).filter(User.openid == openid).one_or_none()
            if not user:
                # 未注册用户首次登录
                user = User(openid=openid, unionid=unionid, balance_id=-1, gender=2, status=User.STATUS_LOGIN,
                            state=User.STATE_NOT_CERTIFICATION, score=0, description="首次登录")
                session.add(user)
                session.flush()

                balance = Balance(user_id=user.id, amount=0, deposit=0, state=Balance.STATE_NORMAL)
                session.add(balance)
            data["user_id"] = user.id

            session_id = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
            user_session = session.query(Session).filter(Session.user_id == user.id).one_or_none()
            # 用户未登录过
            if not user_session:
                user_session = Session(user_id=user.id, session_id=session_id, wx_session_key=session_key)
                session.add(user_session)
            else:
                user_session.session_id = session_id
                user_session.wx_session_key = session_key
                user.status = User.STATUS_LOGIN
            data["session_id"] = session_id

        self.response(RESPONSE_STATUS_SUCESS, RESPONSE_MESSAGE_SUCESS, data=data)

    def data_received(self, chunk):
        pass
