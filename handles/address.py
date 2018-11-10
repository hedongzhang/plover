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
from utiles.exception import PlException


class AddressHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            id = self.get_argument("id")

            with open_session() as session:
                address = session.query(Address).filter(Address.id == id).one()

                data = dict()
                data["id"] = address.id
                data["first_address"] = address.first_address
                data["last_address"] = address.last_address
                data["nick_name"] = address.nick_name
                data["phone"] = address.phone

            self.response(data)
        except Exception as e:
            self.response_error(e)

    def post(self):
        try:
            necessary_list = ["user_id", "type", "property", "first_name", "last_name", "phone", "first_address",
                              "last_address", "latitude", "longitude", "default"]
            request_args = self.post_request_args(necessary_list=necessary_list)

            with open_session() as session:
                default_address = session.query(Address).filter(Address.user_id == request_args["user_id"],
                                                                Address.default == True).one_or_none()
                if request_args["default"] and default_address:
                    default_address.default = False

                address = Address(
                    user_id=request_args["user_id"],
                    type=request_args["type"],
                    property=request_args["property"],
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

            self.response()
        except Exception as e:
            self.response_error(e)

    def put(self):
        try:
            necessary_list = ["id"]
            request_args = self.post_request_args(necessary_list=necessary_list)

            with open_session() as session:
                address = session.query(Address).filter(Address.id == request_args["id"]).one()

                if request_args["default"]:
                    default_address = session.query(Address).filter(Address.user_id == address.user_id,
                                                                    Address.default == True).one_or_none()
                    if default_address:
                        default_address.default = False

                properties = ["user_id", "type", "property", "first_name", "last_name", "phone", "first_address",
                              "last_address", "latitude", "longitude", "default"]

                for property in properties:
                    if property in request_args:
                        address.__setattr__(property, request_args[property])

            self.response()
        except Exception as e:
            self.response_error(e)

    def delete(self, *args, **kwargs):
        try:
            necessary_list = ["id"]
            request_args = self.post_request_args(necessary_list=necessary_list)

            with open_session() as session:
                address = session.query(Address).filter(Address.id == request_args["id"]).one_or_none()
                if address:
                    session.delete(address)

            self.response()
        except Exception as e:
            self.response_error(e)


class AddressDefaultHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            user_id = self.get_argument("user_id")

            with open_session() as session:
                address = session.query(Address).filter(Address.user_id == user_id,
                                                        Address.default == True).one_or_none()
                if address:
                    data = dict()
                    data["id"] = address.id
                    data["first_address"] = address.first_address
                    data["last_address"] = address.last_address
                    data["nick_name"] = address.nick_name
                    data["phone"] = address.phone
                else:
                    raise PlException("This user have no default address !")

            self.response(data)
        except Exception as e:
            self.response_error(e)


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

            data = dict()

            with open_session() as session:
                query = session.query(Address)
                query = query.filter(Address.user_id == user_id)

                if type:
                    query = query.filter(Address.type == type)
                if property:
                    query = query.filter(Address.property == property)
                if default:
                    query = query.filter(Address.default == default)

                data["count"] = query.count()
                query = query.limit(limit)
                query = query.offset(offset)

                data["address_list"] = list()
                for address in query.all():
                    address_info = dict()
                    address_info["id"] = address.id
                    address_info["type"] = address.type
                    address_info["first_name"] = address.first_name
                    address_info["last_name"] = address.last_name
                    address_info["phone"] = address.phone
                    address_info["property"] = address.property
                    address_info["first_address"] = address.first_address
                    address_info["last_address"] = address.last_address
                    address_info["default"] = address.default

                    data["address_list"].append(address_info)

            self.response(data)
        except Exception as e:
            self.response_error(e)
