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
            upload_path = config.get("upload_path")  # 文件的存放路径
            file_metas = self.request.files.get('file', None)
            session_id = self.get_argument("session_id")
            user_id = self.get_argument("user_id")

            if not file_metas or not session_id or not user_id:
                raise PlException('上传文件错误, 无效的参数')

            data = dict(path="")
            for meta in file_metas:
                filename = user_id + "-IDCard-" + meta['filename']
                file_path = os.path.join(upload_path, filename)

                with open(file_path, 'wb') as up:
                    up.write(meta['body'])

                data["path"] += "," + file_path if data["path"] else file_path

            self.response(data=data)
        except ParameterInvalidException as e:
            self.response_request_error(e)
        except Exception as e:
            self.response_server_error(e)


