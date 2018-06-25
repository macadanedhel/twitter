import ConfigParser
import datetime
from langdetect import detect
from nltk.corpus import stopwords
import string
import unicodedata
import re

class speaking:

    emoticons_str = r"""
        (?:
            [:=;xX][oO\-]?[D\)\]\(\]/\\OpPXx]
        )"""
    regex_str = [
        emoticons_str,
        r'<[^>]+>',  # HTML tags
        r'(?:@[\w_]+)',  # @-mentions
        r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
        r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs
        r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
        r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
        r'(?:[\w_]+)',  # other words
        r'(?:\S)'  # anything else
    ]
    #acento_re=re.compile()
    tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE | re.UNICODE)
    emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE | re.UNICODE)
    langvalues=['en','es']
    gbwords=['rt', 'via', 'RT', 'VIA']
    languages={'en':'english','es':'spanish'}
    # -----------------------------------------------------------------------------------------------------------------------
    def tokenize(self, s):
        s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore')
        return self.tokens_re.findall(s)
    # -----------------------------------------------------------------------------------------------------------------------
    def preprocess(self, s, lowercase=False):
        # QUITA LOS EMOTIS
        tokens = self.tokenize(s)
        if lowercase:
            tokens = [token.lower() for token in tokens if not self.emoticon_re.search(token) ]
        return tokens
    # -----------------------------------------------------------------------------------------------------------------------
    def lang_process (self, s, lang=None, users=None, hash=None, words=None, bigram=None):
        if lang in self.langvalues:
            lang=self.languages[lang]
        else:
            #print ('Language {} not supported\nusing english'.format(lang))
            lang = self.languages['en']
        punctuation = list(string.punctuation)
        stop = stopwords.words(lang) + punctuation + self.gbwords
        data={}
        if words:
            data['words']=[term for term in self.preprocess(s, True) if term not in stop and not term.startswith(('#', '@', 'http://t.co/', 'https://t.co/'))]
        if hash:
            data['hash']=[term for term in self.preprocess(s, True) if term not in stop and term.startswith('#')]
        if users:
            data['user']=[term for term in self.preprocess(s, True) if term not in stop and term.startswith('@')]
        if bigram:
            from nltk import bigrams
            data['bigrams']=list(bigrams([term for term in self.preprocess(s) if term not in stop]))
        return (data)