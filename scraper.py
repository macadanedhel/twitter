#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=utf8
import datetime
import os,sys
import ConfigParser
import logging
import argparse
from twist.httptw import *


USERCONFIG = "config/userdata.ini"
ENVCONFIG = "config/env.ini"

def options():
    """ Parse arguments
    """
    parser = argparse.ArgumentParser(
        prog="pwt",
        usage="python %(prog)s [options]",
        description='A new gossip tool',
        epilog='comments > /dev/null'
    )
    ap = argparse.ArgumentParser(prog="scraper",
                                 usage="python3 %(prog)s [options]",
                                 description="TWINT - An Advanced Twitter Scraping Tool.")

    parser.add_argument('--debug',  "-d", action='store_true', help='Debug')

    parser.add_argument('--userWEB', "-uw", action='store_true', help='Search user data in the public page')
    parser.add_argument('--tweetsWEB', "-tw", action='store_true', help='Search tweets in the public page')

    args = parser.parse_args()
    return args

def config_log (fileconf):
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

    logger = logging.getLogger("{}".format(sys.argv[0]))
    logger.setLevel(logging.INFO)
    logger.info("Prueba")
    return logger

def main():
    args = options()
    if args.debug:
        logger = config_log(ENVCONFIG)
    if args.userWEB:
        scraper = scrapbase(ENVCONFIG, True, args.debug)
        res = scraper.searchUSER('macarionull', 1)
        dt = datetime.datetime.now()
        #print (res['user'])
        total = datetime.datetime.now() - dt
        print ("tiempo {}".format(total))
    elif args.tweetsWEB:
        scraper = scrapbase(ENVCONFIG, True, args.debug)
        res = scraper.searchTweets('macarionull')

if __name__ == '__main__':
    options()
    main()



from bs4 import BeautifulSoup
#
# scraper = scrapbase(ENVCONFIG, True)
# res = scraper.searchUSER('macarionull', 1)
# html = res['html']
#
# position = html.find_all("li", "js-stream-item")[-1]["data-item-id"]
#
# all_tweets=[]
# timeline = html.select('#timeline li.stream-item')
#
# for tweet in timeline:
#     _tweet = tweet(False, ENVCONFIG )
#     twt = _tweet.tweets(tweet)
#     tweet_id = tweet['data-item-id']
#     print (twt)
#     print ("---------------------")
#     print ("".format(twt))
#     print ("---------------------")
#
#
#     all_tweets.append({"id": tweet_id, "text": _tweet.data['text']})
#     print( len(all_tweets) )
#     if len(all_tweets) >5:
#         exit(0)

