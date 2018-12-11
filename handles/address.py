#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/3

Author: 

Description: 

"""

from handles.base import BasicHandler
from model.base import open_session
from model.schema import Address
from utiles.exception import ParameterInvalidException, PlException
from utiles import logger

properties = ["user_id", "type", "property", "shop_name", "first_name", "last_name", "phone",
              "first_address", "last_address", "latitude", "longitude", "default"]


class AddressHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            id = self.get_argument("id")

            with open_session() as session:
                address = session.query(Address).filter(Address.id == id,
                                                        Address.state == Address.STATE_NORMAL).one_or_none()
                if not address:
                    raise PlException("此地址不存在！")

                data = dict()
                data["id"] = address.id
                data["user_id"] = address.user_id
                data["type"] = address.type
                data["property"] = address.property
                data["shop_name"] = address.shop_name
                data["first_name"] = address.first_name
                data["last_name"] = address.last_name
                data["phone"] = address.phone
                data["first_address"] = address.first_address
                data["last_address"] = address.last_address
                data["latitude"] = address.latitude
                data["longitude"] = address.longitude
                data["default"] = address.default

            self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)

    def post(self):
        try:
            request_args = self.request_args(necessary_list=properties)

            with open_session() as session:
                default_address = session.query(Address).filter(Address.user_id == request_args["user_id"],
                                                                Address.type == request_args["type"],
                                                                Address.state == Address.STATE_NORMAL,
                                                                Address.default == True).one_or_none()
                if request_args["default"] and default_address:
                    default_address.default = False

                address = Address(
                    user_id=request_args["user_id"],
                    type=request_args["type"],
                    property=request_args["property"],
                    shop_name=request_args["shop_name"],
                    first_name=request_args["first_name"],
                    last_name=request_args["last_name"],
                    phone=request_args["phone"],
                    first_address=request_args["first_address"],
                    last_address=request_args["last_address"],
                    latitude=request_args["latitude"],
                    longitude=request_args["longitude"],
                    default=request_args["default"]
                )
                session.add(address)
                session.flush()

            data = dict(id=address.id)
            self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)

    def put(self):
        try:
            necessary_list = ["id"]
            request_args = self.request_args(necessary_list=necessary_list)

            with open_session() as session:
                address = session.query(Address).filter(Address.id == request_args["id"]).one_or_none()
                if not address:
                    raise Exception("This address is not exist !")

                if request_args["default"]:
                    default_address = session.query(Address).filter(Address.user_id == address.user_id,
                                                                    Address.type == address.type,
                                                                    Address.state == Address.STATE_NORMAL,
                                                                    Address.default == True).one_or_none()
                    if default_address:
                        default_address.default = False

                for property in properties:
                    if property in request_args:
                        address.__setattr__(property, request_args[property])

            self.response()
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)

    def delete(self, *args, **kwargs):
        try:
            necessary_list = ["id"]
            request_args = self.request_args(necessary_list=necessary_list)

            with open_session() as session:
                address = session.query(Address).filter(Address.id == request_args["id"]).one_or_none()
                if address:
                    address.state = Address.STATE_DELETE

            self.response()
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)


class AddressDefaultHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            user_id = self.get_argument("user_id")

            data = dict(tack_address=None, recive_address=None)

            with open_session() as session:
                default_tack_address = session.query(Address).filter(Address.user_id == user_id,
                                                                     Address.type == Address.TYPE_TACK,
                                                                     Address.default == True).one_or_none()

                if default_tack_address:
                    data["tack_address"] = dict(id=default_tack_address.id)
                    for property in properties:
                        data["tack_address"][property] = default_tack_address.__getattribute__(property)

                default_recive_address = session.query(Address).filter(Address.user_id == user_id,
                                                                       Address.type == Address.TYPE_RECIVE,
                                                                       Address.default == True).one_or_none()

                if default_recive_address:
                    data["recive_address"] = dict(id=default_recive_address.id)
                    for property in properties:
                        data["recive_address"][property] = default_recive_address.__getattribute__(property)

            self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)


class AddressesHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            user_id = self.get_argument("user_id")

            type = self.get_argument("type")
            property = self.get_argument("property")
            default = self.get_argument("default")

            limit = self.get_argument("limit")
            offset = self.get_argument("offset")
            if (limit == "") or (offset == ""):
                raise PlException("分页参数不能为空值")

            data = dict()
            data["address_list"] = list()

            with open_session() as session:
                query = session.query(Address)
                query = query.filter(Address.user_id == user_id, Address.state == Address.STATE_NORMAL)

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
