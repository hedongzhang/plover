#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/12/1

Author: 

Description: 

"""

import xml.etree.ElementTree as ET


def loads(string):
    xml_dick = dict()
    try:
        root = ET.fromstring(string)
        for child in root:
            xml_dick[child.tag] = child.text
    except:
        raise Exception("XML解析失败!")
    return xml_dick


def dumps(xml_dict, root_name="xml"):
    root = ET.Element(root_name)
    for key, value in xml_dict.items():
        el_return_code = ET.SubElement(root, str(key))
        el_return_code.text = str(value)
    return ET.tostring(root)


if __name__ == '__main__':
    print(dumps(dict(a="1", b="2")))