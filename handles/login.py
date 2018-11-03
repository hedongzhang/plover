#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/3

Author: 

Description: 

"""

from handles.base import BasicHandler
from handles.base import RESPONSE_STATUS_SERVER_ERROR, RESPONSE_MESSAGE_SERVER_ERROR
from utiles import config, httpclient
from model.base import open_session
from model.schema import User, Balance


class LoginHandler(BasicHandler):
    def post(self):
        try:
            request_context = self.get_request_args(necessary_list=["secret", "js_code", "appid"])
            code2session_request = dict()
            code2session_request["appid"] = request_context["appid"]
            code2session_request["secret"] = request_context["secret"]
            code2session_request["js_code"] = request_context["js_code"]
            code2session_request["grant_type"] = "authorization_code"

            code2session_response = httpclient.get(config.get("code2session_url"), code2session_request)
            errcode = code2session_response["errcode"]
            if errcode == 0:
                self.user_login(code2session_response)
            if errcode == -1:
                self.response(RESPONSE_STATUS_SERVER_ERROR,
                              RESPONSE_MESSAGE_SERVER_ERROR.format(error_message="微信API服务系统繁忙，请稍候再试"))
            elif errcode == 40029:
                self.response(RESPONSE_STATUS_SERVER_ERROR,
                              RESPONSE_MESSAGE_SERVER_ERROR.format(error_message="code值无效"))
            elif errcode == 45011:
                self.response(RESPONSE_STATUS_SERVER_ERROR,
                              RESPONSE_MESSAGE_SERVER_ERROR.format(error_message="微信API服务频率限制，每个用户每分钟100次"))

        except Exception as e:
            self.response(RESPONSE_STATUS_SERVER_ERROR,
                          RESPONSE_MESSAGE_SERVER_ERROR.format(error_message=e))

    def user_login(self, code2session_response):
        openid = code2session_response["openid"]
        session_key = code2session_response["session_key"]
        unionid = code2session_response["unionid"]

        with open_session() as session:
            user = session.query(User).filter(User.open_id == openid).one_or_none()
            if not user:
                # 未注册用户首次登录
                user = User(openid=openid, unionid=unionid, balance_id=-1, gender=2, status=User.STATUS_LOGIN,
                            state=User.STATE_NOT_CERTIFICATION, score=0, description="首次登录")
                session.add(user)
                session.flush()

                balance = Balance(user_id=user.id, amount=0, deposit=0, state=Balance.STATE_NORMAL)
                session.add(balance)
            else:
                session =

    def data_received(self, chunk):
        pass
