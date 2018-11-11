#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/11

Author: 

Description: 

"""

from handles.base import BasicHandler
from model.base import open_session
from model.schema import Verification
from utiles import random_tool


class VerificationHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            phone = self.get_argument("phone")

            with open_session() as session:
                verification_code = random_tool.random_digits(4)

                verification = session.query(Verification).filter(Verification.phone == phone).one_or_none()
                if verification:
                    verification.verification_code = verification_code
                else:
                    verification = Verification(phone=phone, verification_code=verification_code)
                    session.add(verification)

                # TODO: 调用短信接口，发送短信

                data = dict()
                data["id"] = verification.id
                data["phone"] = verification.phone
                data["verification_code"] = verification.verification_code

                self.response(data)
        except Exception as e:
            self.response_error(e)
