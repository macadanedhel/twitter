# -*- coding: utf-8 -*-
# encoding=utf8

from bs4 import BeautifulSoup
USERCONFIG = "config/userdata.ini"
ENVCONFIG = "config/env.ini"

from twist.format import *
from twist.httptw import *
import copy


scraper = scrapbase(ENVCONFIG, True, 1)
html = scraper.searchUSER('macarionull', 1)['html']

position = html.find_all("li", "js-stream-item")[-1]["data-item-id"]

all_tweets=[]
timeline = html.select('#timeline li.stream-item')
_tweet = tweet.tweet(False, ENVCONFIG )
all=[]
for tw in timeline:
    twt = _tweet.tweets(tw)
    tweet_id = tw['data-item-id']
    print (twt)
    print ("---------------------")
    print ("{}".format(type(twt)))
    print ("---------------------")
    all.append(copy.copy(twt))
    #print all
    print "XXXXXXXXXXXXX"
print
print
print "XXXXXXXXXXXXXXXXXXXXX"
print
print
print all