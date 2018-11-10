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


def random_int(num, start=0):
    return random.randint(start, num)


def random_chinese(count=2):
    return "".join(chr(random.randint(0x4e00, 0x9fa5)) for _ in range(count))


def random_digits(count):
    return "".join(random.choice(string.digits) for _ in range(count))

