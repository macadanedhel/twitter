# -*- coding: utf-8 -*-
# encoding=utf8

import re
from bs4 import BeautifulSoup
import requests
import random
import os, sys
import logging
import ConfigParser
import datetime

from fake_useragent import UserAgent
from twist.format import twuser, tweet

def config_log (fileconf, name):
    Config = ConfigParser.ConfigParser()
    if os.path.exists(fileconf):
        Config.read(fileconf)
    else:
        print ("{0} file not found !!!")
        exit(0)
    logging.basicConfig(filename=(
            Config.get('log', 'path') + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + Config.get('log',
                                                                                                       'name')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    logger = logging.getLogger("{}".format(name))
    logger.setLevel(logging.INFO)
    return logger

user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]

headers = {
    'User-Agent': 'none'
}

def RandomUserAgent():
    try:
        ua = UserAgent()
        return ua.random
    except:
        return random.choice(user_agent_list)

class scrapbase:
    """An interface to twitter web."""

    def __init__(self, userconfig, ssl_verify=True, debug=False):
        """Parameters:
        userconfig: file with data needed by the class.
        ssl_verify: should the certificate being verified
        debug: Debug"""
        Config = ConfigParser.ConfigParser()
        if os.path.exists(userconfig):
            Config.read(userconfig)
        else:
            print ("{0} file not found !!!")
            exit(0)
        self.base = Config.get('scraper', 'base')
        self.search  = Config.get('scraper', 'baseSearch')
        self.error = 0
        self.error_message = ""
        self.ssl_verify = ssl_verify
        self.token = None
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        self.ua=headers
        self.DEBUG = debug
        self.userconfig = userconfig
        if debug:
            self.logger = config_log (userconfig , __name__ )
        self.userdata = ""

    def _page (self, name):
        url = self.base+self.search+name
        if self.DEBUG:
            self.logger.info("BEGIN _page")
        if self.DEBUG:
            self.logger.info("GET {}".format(self.base+self.search+name))
        res = requests.get(url, headers=self.ua)

        html = BeautifulSoup(res.content, "html.parser")
        try:
            resultado = html.find('div', 'SearchEmptyTimeline-emptyDescription').text
            if self.DEBUG:
                self.logger.info("html.find : {0} / {1}".format('div', 'SearchEmptyTimeline-emptyDescription'))
        except:
            if self.DEBUG:
                url = self.base + name
                self.logger.info("GET {}".format(url))
            res = requests.get(url, headers=self.ua)
            html = BeautifulSoup(res.content, "html.parser")
        result=html
        if self.DEBUG:
            self.logger.info("END _page")
        return result

    def searchUSER (self, name, type=0, change=False):
        if self.DEBUG:
            self.logger.info("BEGIN searchUSER")
        if change:
            self.ua= RandomUserAgent()
        result={}
        result['html']=self._page(name)
        result['user']=self._user(type, result['html'])
        if self.DEBUG:
            self.logger.info(result['user'])
        if self.DEBUG:
            self.logger.info("END searchUSER")
        return result

    def _user(self, type, html):
        suser = twuser.twuser(self.DEBUG, self.userconfig)
        suser.createuser(type, html)
        return suser.userdata

    def searchTweets (self, name):
        # cambia el none
        if self.DEBUG:
            self.logger.info("BEGIN searchTweets")
        html = self._page(name)
        position = html.find_all("li", "js-stream-item")[-1]["data-item-id"]
        all_tweets = []
        timeline = html.select('#timeline li.stream-item')
        _tweet = tweet.tweet(self.DEBUG, self.userconfig)
        for tw in timeline:
            x =_tweet._add_tweets(tw)

        if self.DEBUG:
            print (_tweet._num())
            _tweet._display_tweets()
            self.logger.info("num : {}".format(_tweet._num()))
            self.logger.info("END searchTweets")

