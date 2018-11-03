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
        except Exception as e:
            self.response_error(e)


class MessagesHandler(BasicHandler):
    def get(self):
        try:
            session_id = self.get_argument("session_id")
            user_id = self.get_argument("user_id")
            type = self.get_argument("type")
            limit = self.get_argument("limit")
            offset = self.get_argument("offset")

            data = dict()

            with open_session() as session:
                query = session.query(Message).filter(Message.user_id == user_id)
                if type:
                    query = query.filter(Message.type == type)

                data["count"] = query.count()
                query = query.limit(limit)
                query = query.offset(offset)

                data["message_list"] = list()

                for message in query.all():
                    message_info = dict()
                    message_info["id"] = message.id
                    message_info["type"] = message.type
                    message_info["title"] = message.title
                    message_info["context"] = message.context
                    message_info["create_time"] = message.create_time.strftime("%Y-%m-%d %H:%M:%S")

                    data["message_list"].append(message_info)

            self.response(data)
        except Exception as e:
            self.response_error(e)
