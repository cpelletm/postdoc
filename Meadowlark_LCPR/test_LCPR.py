#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE

out = Popen(
    args="nm /home/clement/Postdoc/python/Perso/Meadowlark_LCPR/usbdrvd.dll", 
    shell=True, 
    stdout=PIPE
).communicate()[0].decode("utf-8")

attrs = [
    i.split(" ")[-1].replace("\r", "") 
    for i in out.split("\n") if " T " in i
]

from ctypes import CDLL

functions = [i for i in attrs if hasattr(CDLL("/home/clement/Postdoc/python/Perso/Meadowlark_LCPR/usbdrvd.dll"), i)]

print(functions)