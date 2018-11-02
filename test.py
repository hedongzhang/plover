#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/2

Author: 

Description: 

"""


if __name__ == "__main__":
    from model.base import open_session
    from utiles import logger
    from  model.schema import *

    with open_session() as session:
        users = session.query(User).all()
        for user in users:
            logger.warn(user.to_dict())