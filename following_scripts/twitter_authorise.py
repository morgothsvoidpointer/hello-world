#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 01:14:32 2019

@author: deepthought42
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 11 14:42:20 2019
@author: deepthought42
"""


import sys
import tweepy
import os
userhome = os.path.expanduser('~')
#python_dir=userhome+'/Documents/ThinkTank/library/python/python_other/word_match/'
python_dir=userhome+'/Documents/word_files_dir/'
if not os.path.exists(python_dir): os.makedirs(python_dir)
save_dir=python_dir+'Output/'
if not os.path.exists(save_dir): os.makedirs(save_dir)
if python_dir not in sys.path: sys.path.append(python_dir)


consumer_key = 'xxx'
consumer_secret = 'xxx'
access_token = 'xxx'
access_token_secret = 'xxx'





# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
 
# Creation of the actual interface, using authentication
api = tweepy.API(auth,wait_on_rate_limit=True)


#if need to check rate limits 
#


def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
               yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x
                        
A=api.rate_limit_status()

F1=list(findkeys(A,'remaining'))
F2=list(findkeys(A,'limit'))

for count,f1 in enumerate(F1):
    if not F1[count]==F2[count]:
        print([F1[count],F2[count]])





