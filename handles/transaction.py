#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/12/9

Author: 

Description: 

"""

from handles.base import BasicHandler
from model.base import open_session
from model.schema import Message
from utiles.exception import ParameterInvalidException, PlException
from utiles import logger


class TransactionsHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            user_id = self.get_argument("user_id")

            limit = self.get_argument("limit")
            offset = self.get_argument("offset")
            if (limit == "") or (offset == ""):
                raise PlException("分页参数不能为空值")

            data = dict()
            data["transaction_list"] = list()

            with open_session() as session:
                query = session.query(Address)
                query = query.filter(Address.user_id == user_id)

                if type:
                    query = query.filter(Address.type == type)
                if property:
                    query = query.filter(Address.property == property)
                if default:
                    if default.lower() == "true":
                        query = query.filter(Address.default == True)
                    else:
                        query = query.filter(Address.default == False)

                query = query.order_by(Address.default.desc())
                query = query.order_by(Address.create_time.desc())

                data["count"] = query.count()
                query = query.limit(limit)
                query = query.offset(offset)

                for address in query.all():
                    address_info = dict()
                    address_info["id"] = address.id
                    address_info["user_id"] = address.user_id
                    address_info["type"] = address.type
                    address_info["property"] = address.property
                    address_info["shop_name"] = address.shop_name
                    address_info["first_name"] = address.first_name
                    address_info["last_name"] = address.last_name
                    address_info["phone"] = address.phone
                    address_info["first_address"] = address.first_address
                    address_info["last_address"] = address.last_address
                    address_info["latitude"] = address.latitude
                    address_info["longitude"] = address.longitude
                    address_info["default"] = address.default

                    data["address_list"].append(address_info)

            self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)
