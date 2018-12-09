#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/18

Author: 

Description: 

"""

import os

from conf import config
from handles.base import BasicHandler
from utiles.exception import PlException, ParameterInvalidException
from utiles import logger, random_tool


class UploadHandler(BasicHandler):
    def get(self):
        self.write('''
        <html>
        <head><title>Upload File</title></head>
        <body>
            <form action='file' enctype="multipart/form-data" method='post'>
            <input type='file' name='file'/><br/>
            <input type='submit' value='submit'/>
            </form>
        </body>
        </html>
    ''')

    def post(self):
        try:
            file_metas = self.request.files.get('file', None)
            session_id = self.get_argument("session_id")
            user_id = self.get_argument("user_id")
            type = self.get_argument("type")

            if not file_metas or not session_id or not user_id or not type:
                raise PlException('上传文件错误, 无效的参数')

            if type == "0":
                filename_prefix = user_id + "-IDCard-"
                upload_path = config.get("upload_identify_path")
            elif type == "1":
                filename_prefix = user_id + "-Suggestion-%s-" % random_tool.random_string(8)
                upload_path = config.get("upload_suggestion_path")
            else:
                raise PlException('上传文件错误, 无效的type参数')

            data = dict(path="")
            for meta in file_metas:
                filename = filename_prefix + meta['filename']
                file_path = os.path.join(upload_path, filename)

                with open(file_path, 'wb') as up:
                    up.write(meta['body'])

                data["path"] += "," + file_path if data["path"] else file_path

            self.response(data)
        except ParameterInvalidException as e:
            logger.exception()
            self.response_request_error(e)
        except Exception as e:
            logger.exception()
            self.response_server_error(e)


