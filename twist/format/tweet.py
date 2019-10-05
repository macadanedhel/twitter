# -*- coding: utf-8 -*-
# encoding=utf8
import re
from bs4 import BeautifulSoup
import logging
import os, sys
import logging
import ConfigParser
import datetime
import copy


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



class tweet:
    def __init__(self, debug, userconfig):
        self.data = {
            "text": "",
            "data-user-id" : "",
            "data-name" : "",
            "data-screen-name" : "",
            "retweet" : False,
            "data-item-id" : "",
            "tweet_id" : ""
        }
        self.all_tweets=[]
        self.userconfig=userconfig
        self.DEBUG=debug
        if debug:
            self.logger = config_log (userconfig , __name__ )

    def tweets(self, tweet):
        if self.DEBUG:
            self.logger.info("BEGIN tweets")

        self.data['data-item-id'] = tweet['data-item-id']
        if self.DEBUG:
            self.logger.info("data-item-id:{}".format(self.data['data-item-id']))

        try:
            if tweet.find('span', 'js-retweet-text'):
                self.data['retweet'] = True
            # data_retweeter = tweet.find('div','tweet js-stream-tweet js-actionable-tweet js-profile-popup-actionable dismissible-content original-tweet js-original-tweet tweet-has-context has-cards cards-forward')['data-retweeter']
            # data_screen_name = tweet.find('div','tweet js-stream-tweet js-actionable-tweet js-profile-popup-actionable dismissible-content original-tweet js-original-tweet tweet-has-context has-cards cards-forward')['data-screen-name']
            # data_name = tweet ['data-name']
            # data_id = tweet ['data-user-id']
        except:
            pass
        try:
            self.data['data-screen-name'] = tweet.find('div',
                                                 'tweet js-stream-tweet js-actionable-tweet js-profile-popup-actionable dismissible-content original-tweet js-original-tweet tweet-has-context has-cards cards-forward')[
                'data-screen-name']
        except:
            pass
        try:
            self.data['data-name'] = tweet.find('div',
                                          'tweet js-stream-tweet js-actionable-tweet js-profile-popup-actionable dismissible-content original-tweet js-original-tweet tweet-has-context has-cards cards-forward')[
                'data-name']
        except:
            pass
        try:
            self.data['data-user-id'] = tweet.find('div',
                                             'tweet js-stream-tweet js-actionable-tweet js-profile-popup-actionable dismissible-content original-tweet js-original-tweet tweet-has-context has-cards cards-forward')[
                'data-user-id']
        except:
            pass

        #tweet_text = tweet.select('p.tweet-text')[0].get_text()

        self.data['text'] = tweet.select('p.tweet-text')[0].get_text()
        if self.DEBUG:
            self.logger.info("END tweets")
        return (self.data)

    def _add_tweets(self,tw):
        if self.DEBUG:
            self.logger.info("BEGIN _add_tweets")
            self.logger.info("num tweets: {}".format(self._num()))
        aux=self.tweets(tw)
        print aux
        self.all_tweets.append(copy.copy(aux))
        if self.DEBUG:
            self.logger.info("tweet: {}".format(aux))
            self.logger.info("num tweets: {}".format(self._num()))
            self.logger.info("END _add_tweets")
        return aux


    def _num(self):
        return (len(self.all_tweets))

    def _display_tweets(self):
        for tw in self.all_tweets:
            print tw