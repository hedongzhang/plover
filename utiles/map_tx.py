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


def get_distance(from_lat, from_lon, to_locations):
    to_locations = [("%s,%s" % (i["lat"], i["lon"])) for i in to_locations]
    args = {
        "from": ",".join([str(from_lat), str(from_lon)]),
        "to": ";".join(to_locations),
        "key": config.get("map_key_tx")
    }

    response = httpclient.get(config.get("map_url_tx"), args)
    if response["status"] != 0:
        raise Exception("request map server failed status:%s message:%s" % (response["status"], response["message"]))
    else:
        distance = [i["distance"] for i in response["result"]["elements"]]
        return distance
