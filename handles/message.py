#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/3

Author: 

Description: 

"""

from handles.base import BasicHandler
from model.base import open_session
from model.schema import Message
from utiles.exception import ParameterInvalidException, PlException
from utiles import logger


class MessageHandler(BasicHandler):
    def get(self):
        try:
            id = self.get_argument("id")

            with open_session() as session:
                message = session.query(Message).filter(Message.id == id).one()

                data = dict()
                data["id"] = id
                data["type"] = message.type
                data["title"] = message.title
                data["context"] = message.context
                data["create_time"] = message.create_time.strftime("%Y-%m-%d %H:%M:%S")

            self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)

    def post(self):
        try:

            necessary_list = ["user_id", "title", "context", "type", "state"]
            request_args = self.request_args(necessary_list=necessary_list)

            with open_session() as session:
                message = Message(
                    user_id=request_args["user_id"],
                    title=request_args["title"],
                    context=request_args["context"],
                    type=request_args["type"],
                    state=request_args["state"]
                )
                session.add(message)

            self.response()
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)

    def put(self):
        try:
            necessary_list = ["id", "state"]
            request_args = self.request_args(necessary_list=necessary_list)

            with open_session() as session:
                message = session.query(Message).filter(Message.id == request_args["id"]).one_or_none()
                if not message:
                    raise PlException("此消息不存在")
                message.state = request_args["state"]

            self.response()
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)


class MessagesHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            user_id = self.get_argument("user_id")
            type = self.get_argument("type")

            limit = self.get_argument("limit")
            offset = self.get_argument("offset")
            if (limit == "") or (offset == ""):
                raise PlException("分页参数不能为空值")

            data = dict()

            with open_session() as session:
                query = session.query(Message).filter(Message.user_id == user_id)
                if type:
                    query = query.filter(Message.type == type)

                query = query.order_by(Message.create_time.desc())

                data["count"] = query.count()
                query = query.limit(limit)
                query = query.offset(offset)

                data["message_list"] = list()

                for message in query.all():
                    message.state = Message.STATE_READED
                    message_info = dict()
                    message_info["id"] = message.id
                    message_info["type"] = message.type
                    message_info["title"] = message.title
                    message_info["context"] = message.context
                    message_info["create_time"] = message.create_time.strftime("%Y-%m-%d %H:%M:%S")

                    data["message_list"].append(message_info)

            self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)
