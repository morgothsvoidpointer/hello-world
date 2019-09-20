#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 31 14:07:47 2019

@author: deepthought42
"""

import tweepy
import twint
import datetime
import re

import SingleUserExtract

# Consumer keys and access tokens, used for OAuth
consumer_key = 'Xa8XbijTP7F3sg0QJ1QUoLq6f'
consumer_secret = 'cRBjxlQK3PO2cy4zFnfZGlLdtIYm1c9KMIe8IsZVaE0OqFIMsh'
access_token = '1092850952284131328-6prMHiiBPsQHU5In4xho9N1cQy9wpO'
access_token_secret = 'BOs3QPs7PnF8uRMgaexuv3BizPPkMeSdXq3YEqATcIsM9'
# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True)


client_list=['Twitter for iPad', 'Twitter for Android', 'TweetDeck', 'Twitter for iPhone', 'Twitter Web App', 'Twitter Web Client', 'Boris Johnson Plays Tennis', 'Fenix 2', 'Tweetbot for iΟS', 'Mobile Web (M2)', 'Echofon', 'TweetCaster for Android', 'IFTTT', 'Tweetbot for Mac', 'Tweetlogix', 'Buffer', 'Hootsuite Inc.', 'Twitterrific for iOS', 'Flamingo for Android', 'Talon Android', 'Janetter Pro for Android', 'TwitPane for Android', 'boris-bot', 'GBPolBot', 'SocialFlow', 'Facebook', 'Plume\xa0for\xa0Android', 'iOS', 'Blaq for BlackBerry® 10', 'TW Blue', 'Оwly', 'Twitter for Mac', 'Twitter for BlackBerry', 'Talon (Plus)', 'Tweetium for Windows', 'Twidere for Android #7', 'Swat.io', 'Linky for iOS']

#pick a tweet and analyse people who like/retw/reply/quote/replicate it
max_tweets=1000



def get_replies(tweet_id=1169681044573962240,option="twint",interval=None,sources=True,testmode=False):
    if option=="twint":
        #get tweet date and time
        start_status=api.get_status(tweet_id)
        start_time=start_status.created_at
        author=start_status.user.screen_name
    
        profile=[]
        
        b = twint.Config()
        b.Username = author
        b.Since=str(start_time.date())
        b.Store_object=True
        b.Store_object_tweets_list = profile
        b.Hide_output=True
        twint.run.Profile(b)
        
        for entry in profile:
            if entry.id==tweet_id:
                print("found")
                print(vars(entry))
                con_id=entry.conversation_id
        
        if interval==None:
            T=datetime.timedelta(7,0,0,0,0,0)
            
        
        
        end_time=start_time+T
        
        #set up a search
        repl_all=[]
        query_replies="to:@"+author
        c = twint.Config()
        #c.Search = query_replies
        c.Replies=True
        c.To=author
        c.Since=str(start_time.date())
        c.Until=str(end_time.date())
        c.Store_object=True
        c.Store_object_tweets_list = repl_all
        if testmode:
            c.Limit=1
        c.User_full=True
        c.Hide_output=True

        twint.run.Search(c)
        
        A_trial=api.get_status(1170528218702471168)
        
        replies=[]
        for status in repl_all:
            if status.conversation_id==con_id:
                replies.append(status)

                
        status_list=replies
        if sources:
            status_list_s=sources_find(status_list,c,con_id)
        else:
            status_list_s=status_list
        
    return(status_list_s,c)            
 
#this will eventually be a general function that 'updates' twint-obtained lists of objects with either tweepy-obtained ones or with custom twint searches            
def sources_find(status_list,c,conversation_id=None,option="twint"):
    
    print("Warning: if you have a list of retweets, do not use twint, as the dates/sources will be corrupted. You will have to select the tweepy option and fish out each status individually.")
    
    sources_found=[]
    
    for count,status in enumerate(status_list):
        if status_list[count].source=="":
            raw_source_list=[]
            
            
            status_id=status.id
            try:
                status_twp=api.get_status(status_id)
            except tweepy.TweepError:
                print("account "+status.username+" not reachable")
                status_list[count].source="unknown"
            else:
                status_list[count].source=status_twp.source
                if "retweet_date" in vars(status_list[count]):
                    status.retweet_date=status_twp.created_at
            source_twp=status_twp.source
            print(count)
            print("searching for source "+source_twp)
            #if this is done through tweepy, we needn't do anything else
            if option=="twint":
                
                
                #we only run the search once for each client. If it hasn't found everything once, it won't do so again.
                #after the first time, we just add to the list and move on, just doing the tweepy search
                if source_twp not in sources_found:
                    sources_found.append(source_twp)
                    
                    c.Source=source_twp
                    c.Store_object_tweets_list = raw_source_list
                    twint.run.Search(c)
                    
                    source_list=[]            
                    if conversation_id is not None:
        
                        for source_status in raw_source_list:
                            if source_status.conversation_id==conversation_id:
                                source_list.append(source_status)
                    else:
                        source_list=raw_source_list
                        
                    #source_list should be a subset of the original status_list, in the right order. So use it to label entries in status_list
                    counter1=0
                    counter2=0
                    counter_check=0
                    #assume ids in both lists are descending.
                    while counter1<len(status_list) and counter2<len(source_list):
                        id1=status_list[counter1].id
                        id2=source_list[counter2].id
                        if id1==id2:
                            counter_check=counter_check+1
                            status_list[counter1].source=source_list[counter2].source
                            print("match counter1="+str(counter1))
                            print("match counter2="+str(counter2))
                            counter2=counter2+1
                            counter1=counter1+1
        
                        elif id1>id2:
                            counter1=counter1+1
                        elif id2>id1:
                            counter2=counter2+1
                    print("found "+str(counter_check)+" matches")
                    
                    print(sources_found)
    
    src_list=[status.source for status in status_list]
    print(list_multiplicities(src_list))
              
    return(status_list)
                
                
                
                
            
            
            
            
            
    
    
def replies_analyse(replies):
    #analyse by automation vs time
    sources=[]
    times=[]
    for tweet in replies:
        sources.append(tweet.source)
        times.append(tweet.datetime)
        
    return(sources,times)
    
#given a tweet, find users who have retweeted it    
#def get_retweets(tweet_id=1169681044573962240,option="twint",interval=None):
    
    
#def get_likes(tweet_id=1169681044573962240,option="twint",interval=None):
    

def get_copies(tweet_id=1169681044573962240,option="twint",interval=None,word_limit=100,word_limit_low=7):
    print("analysing tweet "+str(tweet_id))
    #split the tweet into sentences. Then search for them, trying to find the original tweet.   
    start_status=api.get_status(tweet_id,tweet_mode="extended")
    start_time=start_status.created_at
    author=start_status.user.screen_name
    print("author "+str(author))
    
    text=url_remove(start_status.full_text)
    #split into sentences
    sentences=text.split(".")
    if len(sentences[-1])==0:
        sentences=sentences[:-1]
    copies_found=[]
    for sentence in sentences:
        if len(sentence)==0:
            continue
        if sentence[0]==' ':
            sentence=sentence[1:]
        
        
        

        
        
        #print(length_w)
        
    #now build a search - this won't work for twint with longer queries, won't work for tweepy for >7 days old posts
        if option=="twint":
            sent_matches=[]
            S=sentence.split(" ")
            length_w=len(S)
            if length_w>word_limit:
                query=" ".join(S[1:word_limit])
            #    query="\""+query+"\""
            else:
                query=sentence
            #    query="\""+query+"\""           
            if length_w<word_limit_low:
                continue
            #query='Netanyahu West Bank Palestinian'
            #query=query+" (@"+author+")"
            bs=twint.Config()
            bs.Search=query
            print("searching "+bs.Search)
            bs.Store_object=True
            bs.Filter_retweets=False
            bs.Store_object_tweets_list = sent_matches
            #bs.Output=False
            twint.run.Search(bs)
            
            #add filter:nativeretweets for retweets
            
        if option=="tweepy":
            copies_found = [status for status in tweepy.Cursor(api.search, q=sentence, tweet_mode='extended').items(max_tweets)]

        
        copies_found.append(sent_matches)
        
        for copy in copies_found:
            print(len(copy))
    return(copies_found)

def get_retweets(tweet_id=1169681044573962240,option="twint",interval=None,word_limit=100,word_limit_low=7):
    
    search_objects_record=[]
    
    print("analysing tweet "+str(tweet_id))
    #split the tweet into sentences. Then search for them, trying to find the original tweet.   
    start_status=api.get_status(tweet_id,tweet_mode="extended")
    start_time=start_status.created_at
    author=start_status.user.screen_name
    print("author "+str(author))
    
    
    
    
    text=url_remove(start_status.full_text)
    #split into sentences
    sentences=text.split(".")
    if len(sentences[-1])==0:
        sentences=sentences[:-1]
    copies_found=[]
    for sentence in sentences:
        if len(sentence)==0:
            continue
        if sentence[0]==' ':
            sentence=sentence[1:]
        
        
        

        
        
        #print(length_w)
        
    #now build a search - this won't work for twint with longer queries, won't work for tweepy for >7 days old posts
        if option=="twint":
            sent_matches=[]
            S=sentence.split(" ")
            length_w=len(S)
            if length_w>100:
                query=" ".join(S[2:10])
            #    query="\""+query+"\""
            else:
                query=sentence
                
            if length_w<word_limit_low:
                continue
            #    query="\""+query+"\""           
            query=query+" filter:nativeretweets"
            #query='Netanyahu West Bank Palestinian'
            #query=query+" (@"+author+")"
            bs=twint.Config()
            bs.Search=query
            print("searching "+bs.Search)
            bs.Store_object=True
            bs.Filter_retweets=False
            bs.Hide_output=True
            bs.Store_object_tweets_list = sent_matches
            #bs.Output=False
            twint.run.Search(bs)
            
            
            search_objects_record.append(bs)
            #add filter:nativeretweets for retweets
            
        if option=="tweepy":
            copies_found = [status for status in tweepy.Cursor(api.search, q=sentence, tweet_mode='extended').items(max_tweets)]

        
        copies_found.append(sent_matches)
        
    for copy in copies_found:
        print("Found "+str(len(copy))+" tweets")    
    return(copies_found,search_objects_record)

def url_remove(text):
    
    URLless_string = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', text)
    return URLless_string
    
def lists_merge_by_id(status_lists,id_type):

    merged={}
    
    if id_type=="retweet_id":
        for status_list in status_lists:

            for status in status_list:
                rtid=int(status.retweet_id)
                if rtid not in merged.keys():
                    merged[rtid]=status
    
    
    if id_type=="id":
        for status_list in status_lists:

            for status in status_list:
                rtid=status.id
                if rtid not in merged.keys():
                    merged[rtid]=status
    return(list(merged.values()))
     
def list_multiplicities(L):
    S=set(L)
    M=[0]*len(S)
    S1=[]
    for count, s in enumerate(S):
       M[count]=len([l for l in L if l==s])
       S1.append(s)
       
    return(M,S1)
       
#%%    
     
if __name__ == '__main__':
#    tweet_id=1171880864944402432
#    status_list,c=get_replies(tweet_id)
#    status_list=sources_find(status_list,c)
#    sources,times=replies_analyse(status_list)
#    
#    tweet_id=1169681044573962240
#    get_copies(tweet_id=1169681044573962240,option="twint",interval=None)
    
    tweet_id=1174579327083659264
    copies_found=get_copies(tweet_id,option="twint",interval=None)
    
    retweets_found_by_sent,bs=get_retweets(tweet_id,option="twint",interval=None)
    
    #merge into a single definitive list
    
    retweets_found=lists_merge_by_id(retweets_found_by_sent,"retweet_id")
    
    #save to file
    
    
    #users
    user_rt_list=[]
    for retweet in retweets_found:
        user_rt_list.append(retweet.user_rt)
    
    
    #times in the twint object seem to be wrong and have to be fetched via tweepy(?)
    

    
    #sources, automation etc
    #sources don't work on rt's. Return the source of the 'original' tweet instead.
    
    retweets_w_sources=sources_find(retweets_found,bs[0],option="tweepy")
    
        #times
    dates_rt_list=[]
    for retweet in retweets_w_sources:
        dates_rt_list.append(retweet.retweet_date)    
        
    #now analyse the retweeters
    
    #for each, extract the last 100 tweets
    
    id_list_all,text_list_all,hashtags_all,mentions_all,timestamps_all=SingleUserExtract.user_history_extract(user_rt_list,save_file=None,option="twint",query=None,days_back=7,testmode=False,proj_id="retw_anal")
    

    #time distribution vs sentiment
    #time distribution vs source
    #relationships among retweeters
    
    
