    #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 01:08:05 2019

@author: deepthought42
"""
#
import twint
#

#Comments. .Search(c) does not seem to return retweets. .Profile(c) does not return replies, but seems to offer up the retweets. 

#try:
#    from twitter_orig import python_dir, save_dir
#except ImportError:
#    import os
#    import sys
#    userhome = os.path.expanduser('~')
#    #python_dir=userhome+'/Documents/ThinkTank/library/python/python_other/word_match/'
#    python_dir=userhome+'/Documents/word_files_dir/'
#    save_dir=python_dir+'Output/'
#    if python_dir not in sys.path: sys.path.append(python_dir)
#

#c = twint.Config()
#c.Username = "twitter"
#
#twint.run.Search(c)
#c1 = twint.Config()
#c1.Search = "#SocialistSunday -filter:retweets"
#c1.Min_likes = 0
#
#twint.run.Search(c1)

#compare tweepy output with twint


tweets = []

c = twint.Config()

c.Username = "@CaraPac46808618"
#c.Filter_retweets=True
#c.Native_retweets=True
c.Retweets=True
c.Replies=True

#c.Limit = 20
c.Store_object = True
c.Store_object_tweets_list = tweets


twint.run.Search(c)

twint_tweets=tweets

#compare

import SingleUserExtract

account_list=[c.Username]

id_list_all,text_list,hashtags,mentions=SingleUserExtract.user_history_extract(account_list,save_file=save_dir+"temp_user_export.csv")

for i in range(min(len(text_list[0]),len(twint_tweets))):
    print(text_list[0][i])
    print(twint_tweets[i].tweet)



for i in range(48):
    print("tweep ")
    print(text_list[0][i])
    print("\n")
    print("twint ")
    print(twint_tweets[i].tweet)
    print("\n")