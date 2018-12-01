#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/3

Author: 

Description: 

"""

from tornado import gen

from conf import config
from handles.base import executor, BasicHandler
from model.base import open_session
from model.schema import User, Account, Session
from utiles import httpclient, random_tool
from utiles.exception import ParameterInvalidException


class LoginHandler(BasicHandler):
    @gen.coroutine
    def post(self):
        try:
            necessary_list = ["appid", "secret", "js_code"]
            request_context = self.request_args(necessary_list)
            request_context["grant_type"] = "authorization_code"

            if config.get("debug"):
                code2session_response = dict(errcode=0, openid=random_tool.random_int(1024 * 1024 * 1024),
                                             session_key=random_tool.random_string(),
                                             unionid=random_tool.random_int(1024 * 1024 * 1024))
            else:
                code2session_response = yield executor.submit(httpclient.get, url=config.get("code2session_url"),
                                                              args=request_context)

            if code2session_response["errcode"] == 0:
                self.user_login(code2session_response)
            else:
                self.response_server_error("微信API服务访问失败({errcode}:{errmsg})".format(**code2session_response))

        except ParameterInvalidException as e:
            self.response_request_error(e)
        except Exception as e:
            self.response_server_error(e)

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

                account = Account(user_id=user.id, amount=0, deposit=0, state=Account.STATE_NORMAL)
                session.add(account)
                session.flush()
                user.account_id = account.id

            session_id = random_tool.random_string()
            user_session = session.query(Session).filter(Session.user_id == user.id).one_or_none()
            # 用户未登录过
            if not user_session:
                user_session = Session(user_id=user.id, session_id=session_id, wx_session_key=session_key)
                session.add(user_session)
            else:
                user_session.session_id = session_id
                user_session.wx_session_key = session_key
                user.status = User.STATUS_LOGIN

            data["user_id"] = user.id
            data["session_id"] = session_id

        self.response(data=data)

    def data_received(self, chunk):
        pass
