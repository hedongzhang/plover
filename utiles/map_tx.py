#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/12/9

Author: 

Description: 

"""

from decimal import Decimal
from utiles import httpclient
from conf import config


def get_distance(from_lat, from_lon, to_lat, to_lon):
    args = {
        "from": ",".join([str(from_lat), str(from_lon)]),
        "to": ",".join([str(to_lat), str(to_lon)]),
        "key": config.get("map_key_tx")
    }

    response = httpclient.get(config.get("map_url_tx"), args)
    if response["status"] != 0:
        raise Exception("request map server failed status:%s message:%s" % (response["status"], response["message"]))
    else:
        distance = response["result"]["elements"][0]["distance"]
        if distance < 1000:
            return "%sm" % distance
        else:
            distance_str = (Decimal(str(distance)) / Decimal("1000")).quantize(Decimal('0.00'))
            return "%skm" % distance_str
