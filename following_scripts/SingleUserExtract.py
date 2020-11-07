#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 11 14:42:20 2019
@author: deepthought42
"""


from tweepy import Cursor
from datetime import datetime, timedelta
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
#import datetime

import tweepy
import twint
from wordcloud import WordCloud, STOPWORDS
import nltk_functions
import webbrowser

import nest_asyncio
nest_asyncio.apply()

import patel1


from twitter_authorise import api, auth, save_dir, userhome, python_dir
from twitter_orig_utils import list_flat

def user_history_extract(account_list,save_file=None,option="tweepy",query=None,days_back=10000,testmode=False,proj_id="users_ss"):
    
    if (isinstance(query,list)):
        query=keyword_OR_query_construct(query)
    
    
    id_list_all=[]
    text_list_all=[]
    mentions_all=[]
    hashtags_all=[]
    timestamps_all=[]
    
    if option=="tweepy":
        
        if len(account_list) > 0:
          for target in account_list:
              
            status_list=[]
            text_list=[]
            id_list=[]
              
            print("Getting data for " + target)
            try:
                item = api.get_user(target)
            except tweepy.TweepError:
                id_list_all.append([])
                text_list_all.append([])
                hashtags_all.append([])
                mentions_all.append([])
                timestamps_all.append([])
                continue
            print("name: " + item.name)
            print("screen_name: " + item.screen_name)
            print("description: " + item.description)
            print("statuses_count: " + str(item.statuses_count))
            print("friends_count: " + str(item.friends_count))
            print("followers_count: " + str(item.followers_count))
            
            
          # to calculate things like time deltas with.
        
            tweets = item.statuses_count
            account_created_date = item.created_at
            delta = datetime.utcnow() - account_created_date
            account_age_days = delta.days
            print("Account age (in days): " + str(account_age_days))
            if account_age_days > 0:
              print("Average tweets per day: " + "%.2f"%(float(tweets)/float(account_age_days)))
            
            
            
            hashtags = []
            mentions = []
            timestamps=[]
            tweet_count = 0
            end_date = datetime.utcnow() - timedelta(days=days_back)
            
            try:
                if query is None:
                    status_list=[status for status in Cursor(api.user_timeline, id=target).items()]
                else:
                    query_tot="from:"+target+" "+query
                    
                    status_list=[status for status in Cursor(api.search,q=query_tot, tweet_mode='extended').items()]
            
            except tweepy.TweepError as err:   
                print("user not responsive, error code "+str(err.api_code))
                id_list_all.append([])
                text_list_all.append([])
                hashtags_all.append([])
                mentions_all.append([])
                timestamps_all.append([])
            else:
                for status in status_list:
                  tweet_count += 1
                  timestamps.append(status.created_at)
                  if hasattr(status, "entities"):
                    entities = status.entities
                    if "hashtags" in entities:
                      for ent in entities["hashtags"]:
                        if ent is not None:
                          if "text" in ent:
                            hashtag = ent["text"]
                            if hashtag is not None:
                              hashtags.append(hashtag)
                    if "user_mentions" in entities:
                      for ent in entities["user_mentions"]:
                        if ent is not None:
                          if "screen_name" in ent:
                            name = ent["screen_name"]
                            if name is not None:
                              mentions.append(name)
                    id_list.append(status.id)
                    try:
                        text_list.append(status.full_text)
                    except AttributeError:
                        text_list.append(status.text)
                  if status.created_at < end_date:
                    break
            

                else:
                    print
                    print("Most mentioned Twitter users:")
                    for item, count in Counter(mentions).most_common(10):
                      print(item + "\t" + str(count))
                 
                    print
                    print("Most used hashtags:")
                    for item, count in Counter(hashtags).most_common(10):
                      print(item + "\t" + str(count))
                 
                    print
                    print("All done. Processed " + str(tweet_count) + " tweets.")
                    print
                    
                    id_list_all.append(id_list)
                    text_list_all.append(text_list)
                    hashtags_all.append(hashtags)
                    mentions_all.append(mentions)
                    timestamps_all.append(timestamps)
                    #write status_list to file
                    if save_file is not None:
                        patel1.append_json(status_list,save_file)
    elif option=="twint":
        if len(account_list) > 0:
          for target in account_list:
            user_dump=[]
            user_dump.append(save_dir+proj_id+"/"+target+"_userinfo.json")
              
            print("Getting data for " + target) 
            status_list=[]
            text_list=[]
            id_list=[]
              
            l_temp=[]
            c = twint.Config()
            c.Username=target
            c.Store_object=True
            c.Profile=True
            c.Store_object_tweets_list = l_temp
            c.Store_json=True
            c.Hide_output = True
            c.Output = user_dump
            

            
            try:
                #if a query is specified, we search for account name(s) with the query
                if query is not None:
                    c.Search=query
                    twint.run.Search(c)
                    print(len(l_temp))
                #but if not, we look for the user history, including the replies they wrote. The aim may be to then search for the query offline.
                else:
                    c.Get_replies = True
                    twint.run.Search(c)
                    #twint.run.Profile(c) not working atmo
                #if we find nothing
                c2 = twint.Config()
                c2.Username = target
                c2.Store_object=True
                twint.run.Lookup(c2)
                item=twint.output.users_list[-1]
                

                
            except:
                print("some error scraping")
                
                id_list_all.append([])
                text_list_all.append([])
                hashtags_all.append([])
                mentions_all.append([])
                timestamps_all.append([])
                continue
            
            

            
            
            
            print("name: " + item.name)
            print("screen_name: " + item.username)
            print("description: " + item.bio)
            #print("statuses_count: " + str(item["statuses_count"]))
            #print("friends_count: " + str(item.friends_count))
            print("followers_count: " + str(item.followers))
            
            
          # to calculate things like time deltas with.
        

            tweets = item.tweets
            account_created_date = item.join_date
            account_created_time = item.join_time
            account_created=datetime.strptime(account_created_date+" "+account_created_time,'%d %b %Y %I:%M %p')                          
            delta = datetime.utcnow() - account_created
            account_age_days = delta.days
            print("Account age (in days): " + str(account_age_days))
            if account_age_days > 0:
              print("Average tweets per day: " + "%.2f"%(float(tweets)/float(account_age_days)))
            
            
            
            hashtags = []
            mentions = []
            timestamps =[]
            tweet_count = 0
            end_date = datetime.utcnow() - timedelta(days=days_back)
            try:
                for status in l_temp:
                  tweet_count += 1
                  timestamps.append(datetime.fromtimestamp(status.datetime/1000))
                  if hasattr(status, "hashtags"):
                    for hashtag in status.hashtags:
                      hashtags.append(hashtag)
                  if hasattr(status, "mentions"):
                    for mention in status.mentions:
                      mentions.append(mention)
                  status_list.append(status)
                  id_list.append(status.id)
                  text_list.append(status.tweet)
                  if datetime.fromtimestamp(status.datetime/1000) < end_date:
                    break
            
            except tweepy.TweepError as err:   
                print("user not responsive, error code "+str(err.api_code))
                id_list_all.append([])
                text_list_all.append([])
                hashtags_all.append([])
                mentions_all.append([])
                timestamps_all.append([])
            else:
                print
                print("Most mentioned Twitter users:")
                for item, count in Counter(mentions).most_common(10):
                  print(item + "\t" + str(count))
             
                print
                print("Most used hashtags:")
                for item, count in Counter(hashtags).most_common(10):
                  print(item + "\t" + str(count))
             
                print
                print("All done. Processed " + str(tweet_count) + " tweets.")
                print
                
                id_list_all.append(id_list)
                text_list_all.append(text_list)
                hashtags_all.append(hashtags)
                mentions_all.append(mentions)
                timestamps_all.append(timestamps)
                #write status_list to file
                #if save_file is not None:
                    #patel1.append_json(status_list,save_file)
            
    if testmode:
        return(status_list,text_list_all,hashtags_all,mentions_all,timestamps_all)

    else:
        return(id_list_all,text_list_all,hashtags_all,mentions_all,timestamps_all)

def keyword_OR_query_construct(keywords):
    kw=[]
    for count, keyword in enumerate(keywords):
        if " " in keyword:
            kw.append("\""+keyword+"\"")
        else:
            kw.append(keyword)
    
    query=" OR ".join(kw)
    return(query)

def line_breaks_add(filename):
    with open(filename,"r") as f:
        s=f.readlines()

def url_recreate(user,post_id,open_in_browser=False,tabs_open_counter=0):
    url="https://twitter.com/"+user+"/status/"+str(post_id)
    webbrowser.open(url, new=2, autoraise=True)
    tabs_open_counter=tabs_open_counter+1
    return(url,tabs_open_counter)
    
    
#word cloud representing the user's posts
        
def word_cloud_history(text_list):
    stop_words = ["https", "co", "RT","twitter","tweet","retweet","link","posted","pic","tho","tbh","bit","ur","cos","pictwittercom"] + list(STOPWORDS) + patel1.load_json("stopwords-iso.json")
    #prune all links
    
    for count,text in enumerate(text_list):
        text_list[count]=re.sub(r"http\S+", "", text)
        text_list[count]=re.sub(r"https\S+", "", text)
        
    words=" ".join(text_list)
    wordcloud_local = WordCloud(stopwords=stop_words, background_color="white",height=400,width=800,max_words=500).generate(words)
    plt.imshow(wordcloud_local, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    wordcloud_local.to_file(save_dir+"wc.png")
    return(stop_words)

#runs the text through a word graph setup
def text_process(text_list,stopwords):#
    import word_graphs
    ret=word_graphs.process_raw_data("None",stopwords,input_object=text_list)
    tokens=word_graphs.tokenize_sentences(ret,stopwords)
    cleaned=word_graphs.clean_sentences(tokens,stopwords,remove_possessive=True)
    frequencies=word_graphs.get_word_frequencies(cleaned,stopwords)
    N=word_graphs.nounlist_construct(frequencies,tokens,stopwords)
    return(N[0],N[1],N[2],tokens,cleaned)
    
def time_hist(occurance_list):
    O=np.array(occurance_list)
    frame=pd.Series(O[0])
    (frame. # use date-time as index
     apply(lambda x: x.day).
     plot.bar()) # make a barplot

def extra_clean(all_cleaned):
    cleaned_tokens=[]
    slang_dict={}
    slang_dict["ppl"]="people"
    slang_dict["yrs"]="years"
    slang_dict["tht"]="that"
    slang_dict["obv"]="obviously"
    slang_dict["b/c"]="because"
    for clean in all_cleaned:
        if clean in slang_dict.keys():
            clean=slang_dict[clean]
        cl=re.sub("@","",clean)
        cll=cl.split("/")
        if "w" in cll:
            cll=["with" if x=="w" else x for x in cll]
        cleaned_tokens.extend(cll)
    return(cleaned_tokens)

def barplot(word_list):
    import itertools
    wchain=list(itertools.chain(*[word_list]))
    
    import collections
    counter=collections.Counter(wchain)
    
    C=counter.most_common(100)
    P=pd.DataFrame(C,columns=["words","count"])
    P.head()
    
    fig, ax = plt.subplots(figsize=(8, 16))

    # Plot horizontal bar graph
    P.sort_values(by='count').plot.barh(x='words',
                          y='count',
                          ax=ax,
                          color="purple")
    
    ax.set_title("Common Words Found in Tweets (Including All Words)")
    
    plt.show()

    

#%%     
# Driver code 
