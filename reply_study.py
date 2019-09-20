#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 00:21:13 2019

@author: deepthought42
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""



import tweepy
import bokeh
import datetime
import csv
import matplotlib
import math
#import pillow
import wordcloud
import networkx
import graphviz
import re
import numpy as np
import pandas as pd
from collections import Sequence
from itertools import chain, count
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
import warnings
warnings.filterwarnings("ignore")

import os
import sys 
userhome = os.path.expanduser('~')
#python_dir=userhome+'/Documents/ThinkTank/library/python/python_other/word_match/'
python_dir=userhome+'/Documents/word_files_dir/'
save_dir=python_dir+'Output/'
if python_dir not in sys.path: sys.path.append(python_dir)


# Consumer keys and access tokens, used for OAuth
consumer_key = 'Xa8XbijTP7F3sg0QJ1QUoLq6f'
consumer_secret = 'cRBjxlQK3PO2cy4zFnfZGlLdtIYm1c9KMIe8IsZVaE0OqFIMsh'
access_token = '1092850952284131328-6prMHiiBPsQHU5In4xho9N1cQy9wpO'
access_token_secret = 'BOs3QPs7PnF8uRMgaexuv3BizPPkMeSdXq3YEqATcIsM9'

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
 
# Creation of the actual interface, using authentication
api = tweepy.API(auth,wait_on_rate_limit=True)




def replies_find(username):
    name=username
    replies=[] 
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)  
    for full_tweets in tweepy.Cursor(api.user_timeline,screen_name=name,timeout=999999).items(10):
      for tweet in tweepy.Cursor(api.search,q='to:'+name,result_type='recent',timeout=999999).items(1000):
        if hasattr(tweet, 'in_reply_to_status_id_str'):
          if (tweet.in_reply_to_status_id_str==full_tweets.id_str):
            replies.append(tweet.text)
      print("Tweet :",full_tweets.text.translate(non_bmp_map))
      for elements in replies:
           print("Replies :",elements)
      replies.clear()
      
if __name__ == '__main__':
    uname="OwenJones84"
    replies_find(uname)