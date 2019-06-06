#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=utf8

from twist.httptw import *

USERCONFIG = "config/userdata.ini"
ENVCONFIG = "config/env.ini"

scraper = scrapbase(ENVCONFIG)
print (scraper.base)
res=scraper._searchUSER('macadanedhel')
print res['status_code']
file = "trapi.txt"
f = open(file, 'w')
f.write(res['content'])
f.close()

