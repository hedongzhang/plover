#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/11

Author: 

Description: 

"""

from datetime import datetime, timedelta
from tornado import gen

from handles.base import BasicHandler, executor
from model.base import open_session
from model.schema import Verification
from utiles import random_tool, logger
import utiles.sms_xa as sms
from utiles.exception import ParameterInvalidException, PlException


class VerificationHandler(BasicHandler):
    @gen.coroutine
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            phone = self.get_argument("phone")

            with open_session() as session:
                verification_code = random_tool.random_digits(4)

                verification = session.query(Verification).filter(Verification.phone == phone).one_or_none()
                if verification:
                    if datetime.now() < verification.update_time + timedelta(minutes=1):
                        raise PlException("上次获取验证码不足一分钟, 请稍后重试")
                    else:
                        verification.verification_code = verification_code
                        verification.count += 1
                else:
                    verification = Verification(phone=phone, verification_code=verification_code, count=1)
                    session.add(verification)

                # 调用短信接口，发送短信
                _ = yield executor.submit(sms.send_verification_code, business_id=session_id, phone_numbers=phone,
                                          code=verification_code)

                data = dict()
                data["id"] = verification.id
                data["phone"] = verification.phone
                data["verification_code"] = verification.verification_code

                self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)
