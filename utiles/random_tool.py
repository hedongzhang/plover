#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/11/3

Author: 

Description: 

"""
import string
import random


def random_string(count=32):
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(count))

def random_int(num):
    return random.randint(0, num)
