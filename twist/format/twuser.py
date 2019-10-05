# -*- coding: utf-8 -*-
# encoding=utf8
import re
from bs4 import BeautifulSoup
from datetime import datetime
import logging

class twuser:
    def __init__(self, debug, userconfig):
        self.userdata = {
            "id" : 0,
            "id_str" : "",
            "background_image": "",
            "name": "",
            "screen_name": "",
            "url_user_home": "",
            "tweets": 0,
            "following": 0,
            "followers": 0,
            "protected_tweets": False,
            "verified_account": False,
            "likes": 0,
            "lists": 0,
            "bio" : "",
            "location" : "",
            "media_count" : 0,
            "avatar" : "",
            "born" : "",
            "created_at" : ""
        }
        self.ID=0
        # Data from search page
        self.MINu=0
        # Data from main page
        self.URLu=1
        # Data from twitter
        self.KEYu=2
        self.publicTwitter = True
        self.userconfig=userconfig
        self.DEBUG=debug

    def _verified (self,type,html):
        if type < self.KEYu:
            try:
                is_verified = html.find("span", "ProfileHeaderCard-badges").text
                if "Verified account" in is_verified:
                    self.userdata['verified_account'] = True
                else:
                    self.userdata['verified_account'] = False
            except:
                self.userdata['verified_account'] = False
        else:
            pass

    def _id (self,type, html):
        # id, name, screen_name, protected_tweets
        if type < self.KEYu:
            try:
                group = html.find("div", "user-actions")
            except:
                group = html.find("div", "user-actions btn-group not-following protected")
            self.userdata['id'] = group["data-user-id"]
            self.userdata['name'] = group["data-name"]
            self.userdata['screen_name'] = group["data-screen-name"]
            self.userdata['protected_tweets'] = group["data-protected"]
        else:
            pass

    def _card (self,type, html):
        # bio, location, url_user_home
        if type < self.KEYu:
            try:
                self.userdata['bio'] = html.find("p", "ProfileHeaderCard-bio u-dir").text.replace("\n", " ")
            except:
                self.userdata['bio'] = "None"
            try:
                self.userdata['location'] = html.find("span", "ProfileHeaderCard-locationText u-dir").text
                self.userdata['location'] = self.userdata['location'][15:].replace("\n", " ")[:-10]
            except:
                ret = "None"
            try:
                print html.find("span", "ProfileHeaderCard-urlText u-dir").find("a")["title"]
            except:
                self.userdata['url_user_home'] = "None"
        else:
            pass

    def _stat(self, type, html, _type):
        # 'tweets', 'following', 'followers', 'likes', 'lists',
        if type == self.MINu:
            for i in html.find_all("a",
                                   "ProfileCardStats-statLink u-textUserColor u-linkClean u-block js-nav js-tooltip"):
                res = re.search(_type, str(i))
                if res:
                    self.userdata[_type] = int(i.find("span", "ProfileCardStats-statValue").text)
        elif type == self.URLu:
            try:
                _class = "ProfileNav-item ProfileNav-item--{0}".format(_type)
                stat = html.find("li", _class)
            except:
                pass
            try:
                if _type == 'tweets is-active':
                    _type = 'tweets'
                self.userdata[_type] =  stat.find("span", "ProfileNav-value")["data-count"]
            except:
                pass
        else:
            pass

    def _avatar (self,type,html):
        if type <= self.URLu:
            try:
                self.userdata['avatar'] = html.find("img", "ProfileAvatar-image")['src']
            except:
                pass
        else:
            pass

    def _date (self,type,html):
        if type == self.URLu:
            try:
                datetime_object = datetime.strptime(str(html.find("span", "ProfileHeaderCard-joinDateText js-tooltip u-dir")["title"]).replace(".",""), '%I:%M %p - %d %b %Y')
            except:
                try:
                    datetime_object = datetime.strptime(
                        str(html.find("span", "ProfileHeaderCard-joinDateText js-tooltip u-dir")["data-original-title"]).replace(".",""),
                        '%I:%M - %d %b %Y')
                except:
                    datetime_object = None
            if datetime_object is not None:
                self.userdata['created_at'] =  datetime_object.isoformat()
        else:
            pass

    def _background (self,type,html):
        if type == self.MINu:
            try:
                self.userdata['background_image'] = html.find("div","ProfileCard js-actionable-user ProfileCard--wide").find("a", "ProfileCard-bg js-nav")['style'].split('(')[1].rstrip(');')
            except:
                pass
        elif type == self.URLu:
            try:
                self.userdata['background_image'] = re.sub('\n*\s*\n*', '',
                                               html.find("div", "ProfileCanopy-headerBg").find("img")["src"])
            except:
                pass
        else:
            pass

    def _born (self,type,html):
        try:
            self.userdata['born'] = re.sub('\n*$', '', re.sub('^\n*\s*', '', html.find("div","ProfileCard js-actionable-user ProfileCard--wide").find("span",
                                                                           "ProfileHeaderCard-birthdateText u-dir").text))
        except:
            pass

    def createuser(self,type,html):

        # id, name, screen_name, protected_tweets
        self._id(type,html)
        # bio, location, url_user_home
        self._card(type,html)
        #
        for i in ['tweets is-active', 'following', 'followers', 'likes', 'lists']:
            self._stat(type, html, i)
        # avatar
        self._avatar(type,html)
        #  created_at
        self._date(type, html)
        # background_image
        self._background(type, html)
        #

