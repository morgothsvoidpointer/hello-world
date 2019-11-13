
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 21:38:14 2019
@author: deepthought42
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor
This is a temporary script file.
"""

import sys
import os
from twitter_orig_utils import *
from twitter_authorise import api, auth, save_dir, userhome, python_dir

from SingleUserExtract import user_history_extract, keyword_OR_query_construct
import patel1

import time
import tweepy
import twint
import re
import asyncio
import random


max_follower_count=10000
max_tweets=100000
query1="#SocialistSunday -filter:retweets"
query2="#SocialistAnyDay -filter:retweets"

load_file=1

random_shuffle=1

follow=True
lookup=False
if follow:
    lookup=True

TP="tweepy"

t=8#min no. of people listed in tweet
u=5#max no. of hashtags allowed in tweet
trigger_length=400#character length beyond which we don't just accept every @ but try to omit the mentions at the start

exclude_list={}

wainwright_import=0

try:
    wainwright_list=array_load(save_dir+"problem_users_socialist_sunday.csv")
except UnicodeDecodeError:
    print("wainwright AS list not found")
    wainwright_list=[]


for entry in wainwright_list:
    
    exclude_list['@'+entry[0].lower()]="wainwright list"

#1
exclude_list["@LauraMStuart9".lower()]="anti-LGBT, suspected Labour anti-semite"
exclude_list["@Telco_Diversion".lower()]="strongly suspected holocaust denier"
exclude_list["@angelaissa66".lower()]="zionists control america conspiracist"
exclude_list["@60sparkle".lower()]="Rotschild central bank"
exclude_list["@agoyawear".lower()]="Rotschild bankers"
exclude_list["@Banjomarla".lower()]="Soros conspiracies"
exclude_list["@beholdcosmicwav".lower()]="Rotschild, 9/11 denial"
exclude_list["@bellhappe".lower()]="Rotschild and Soros"
exclude_list["@bel_nagy".lower()]="Soros"
exclude_list["@SilkCutBlue".lower()]="Brexit party sympathiser"
exclude_list["@ISRAEL_PREDATOR".lower()]="NWO"

ignore_posts_from={}

ignore_posts_from['@makinghappyme']="Keeps tagging in non-socialists"
ignore_posts_from['makinghappyme']="Keeps tagging in non-socialists"




query1="#SocialistSunday -filter:retweets"
query2="#SocialistAnyDay -filter:retweets"


    
#Config the twint object
c = twint.Config()

        

def query_tweets(query, lang="en", limit=max_tweets, option="tweepy"):
        """
        returns all the tweets within 7 days top according to the query received by this method
        returns the complete tweet
        :param query: should contain all the words and can include logic operators
        should also provide the period of time for the search
        ex: rock OR axe
        (visit https://dev.twitter.com/rest/public/search to see how to create a query)
        :param lang: the language of the tweets
        :param limit: defines the maximum amount of tweets to fetch
        :return: tweets: a list of all tweets obtained after the request
        """
        
        searched_tweets=[]
        
        
        if option=="tweepy":
            searched_tweets = [status for status in tweepy.Cursor(api.search, q=query, tweet_mode='extended').items(max_tweets)]
        if option=="twint":

            c = twint.Config()
            
            c.Store_object = True
            c.Store_object_tweets_list = searched_tweets
            c.Search=query
            if limit is not None:
                c.Limit=int(limit/20)
            c.Store_csv = True
            c.Hide_output = True
            c.Output = "test_twint.csv"
            asyncio.set_event_loop(asyncio.new_event_loop())
            twint.run.Search(c)
            print("number tweets found for query "+query)
            print(len(searched_tweets))
            print("earliest tweet date ")
            print(searched_tweets[-1].datestamp)
        #print(searched_tweets)
        return(searched_tweets)      


def status_list_prune(status_list,ignore_posts_from=ignore_posts_from):
    ignore_list=ignore_posts_from.keys()
    status_list_new=[]
    if len(status_list)==0:
        return([])
    elif isinstance(status_list[0],twint.tweet.tweet):
        for status in status_list:
            print(type(status_list[0]))
            print(type(status))
            print(status)
            if status.username not in ignore_list:
                status_list_new.append(status)
            else:
                print("post from "+status.username+" ignored")
        
    else:
        for status in status_list:
            if status.author.screen_name not in ignore_list:
                status_list_new.append(status)
            else:
                print("post from "+status.author.screen_name+" ignored")
    return(status_list_new)
    
    
    
    
    
    
def ampersant_extract(status_list,option=0,trigger_length=400):
    dotdotdot="\u2026"
    amper=[]

    if len(status_list)==0:
        return([])
    elif isinstance(status_list[0],twint.tweet.tweet):
        for i in range(len(status_list)):
            amper.append(status_list[i].mentions)
    
    else:
        for i in range(len(status_list)):
            tag_list_status=[]
            
            if isinstance(status_list[i],tweepy.models.Status):
    
                try:
                    tweet=status_list[i].full_text
                except AttributeError:
                    tweet=status_list[i].text
            elif isinstance(status_list[i],str):
                tweet=status_list[i]
                
            cleaned = re.sub(r"[,.:;#?!&$\n\r]+\ *", " ", tweet)
            cleaned_list=cleaned.split(" ")
            if (option):
                if (len(tweet)>trigger_length):
                    for count, entry in enumerate(cleaned_list):
                        if entry.startswith('@'):
                            cleaned_list[count]=""
                        else:
                            break
                            
            for j in range(len(cleaned_list)):
                if (cleaned_list[j].startswith('@') and not cleaned_list[j].endswith(dotdotdot)):
                    tag_list_status.append(cleaned_list[j])
            amper.append(tag_list_status)
    return(amper)
    

    

def hash_extract(status_list):
    tag_list=[]
    if len(status_list)==0:
        return([])
        
    elif isinstance(status_list[0],twint.tweet.tweet):
        for i in range(len(status_list)):
            tag_list.append(status_list[i].hashtags)
    else:
        
        for i in range(len(status_list)):
            tag_list_status=[]
            if isinstance(status_list[i],tweepy.models.Status):
                
                try:
                    tweet=status_list[i].full_text
                except AttributeError:
                    tweet=status_list[i].text
            elif isinstance(status_list[i],str):
                tweet=status_list[i]
            cleaned = re.sub(r"[,.;:@?!&$\n\r]+\ *", " ", tweet)
            cleaned_list=cleaned.split(" ")
            for j in range(len(cleaned_list)):
                if (cleaned_list[j].startswith('#')):
                    tag_list_status.append(cleaned_list[j])
            tag_list.append(tag_list_status)
    return(tag_list)

def full_text_extract(status_list):
    twt_text=[]
    
    if len(status_list)==0:
        return([])
        
    elif isinstance(status_list[0],twint.tweet.tweet):
        for i in range(len(status_list)):
            twt_text.append(status_list[i].tweet)
    else:
        for i in range(len(status_list)):
            try:
                twt_text.append(status_list[i].full_text)
            except AttributeError:
                twt_text.append(status_list[i].text)            
    return(twt_text)
    

def text_show(status_list):
    
    if len(status_list)==0:
        return([])
        
    elif isinstance(status_list[0],twint.tweet.tweet):
        for tweet in status_list:
            print(tweet.tweet)
            
    else:
        for tweet in status_list:
            print(tweet.full_text)


def list_cut(at_list,hashlist,author_list,t=10,u=3):
    at_list_new=[]
    authors_relevant=[]
    c=-1
    for count, at_entry in enumerate(at_list):
        c=c+1
        if len(at_entry)>t and len(hashlist[c])<u:
            at_list_new.append(at_entry)
            if author_list is not None:
                authors_relevant.append(author_list[count])
    return(at_list_new,authors_relevant)

def list_flat(a):
    #return functools.reduce(operator.iconcat, a, [])
    return [item for sublist in a for item in sublist]

def list_freq(flatlist):
    flist={}
    flatlist.sort()
    word_last=""
    new_counter=0
    for word in flatlist:
        if not word==word_last:
            new_counter=0
            flist[word]=1
        else:
            new_counter=new_counter+1
            flist[word]=new_counter
        word_last=word
    return(flist)

def dots_split(flattened_list):
    new_list=[]
    sub_list=[]
    for item in flattened_list:
        if not item.endswith("…"):
            new_list.append(item)
        else:
            item=item[:-1]
            sub_list.append(item)
    rem_list=[]
    for count, item1 in enumerate(sub_list):
        for item2 in flattened_list:
            if item1 in item2:
                break
                rem_list.append(count)
    sub_list_new=[]
    for count, item in enumerate(sub_list):
        if count not in rem_list:
            sub_list_new.append(item)
    return(new_list,sub_list_new)

def users_follow(user_list,friends_names,max_follower_count=10000,follow=False,lookup=False):
    user_data=[]
    superuser_data=[]
    user_failure=[]
    
    ss_excluded=[]
    
    counter=0
    
    
    for user in user_list:
        if user.lower() in [a.lower() for a in exclude_list.keys()]:
            print("user "+user+" not added, "+exclude_list[user.lower()])
            ss_excluded.append(user)
        elif re.sub("@","",user) in friends_names:
                print("user "+user+" on friendlist")                
        else:
            if lookup:
                try:
                    user_get=api.get_user(screen_name=user)
                except tweepy.TweepError:
                    user_failure.append(user)
                    print("user "+user+" threw error")
                    continue
                #print(max_follower_count)
                #print(user_get.followers_count)
                if user_get.followers_count<max_follower_count and user_get.verified==False and user_get.favourites_count>10:
        
                    user_data.append(user_get)
                    
                        
        
                    if follow:
                        if user_get.screen_name in friends_names:
                            print("user "+user_get.screen_name+" on friendlist")
                        else:
                            try:
                                api.create_friendship(user)
        
                            except tweepy.TweepError as err:
                                 if err.api_code==161:
                                     print("waiting on api")
                                     time.sleep(60)
                                     try:
                                        api.create_friendship(user)
                                     except tweepy.TweepError as err:                            
                                        if err.api_code==161:
                                            print("you'll have a longer wait")
                                            time.sleep(300)
                                            try:
                                                api.create_friendship(user)
                                            except tweepy.TweepError as err:
                                                if err.api_code==161:
                                                    print("timeout-aborting early")
                                                    print("total number of friends made is "+str(counter))
                                                    return(user_data,superuser_data,user_failure,ss_excluded)                                            
                                     else:
                                         counter=counter+1
                                         print("friended user "+user_get.screen_name+", friended user count"+str(counter))
                                         
                                 elif err.api_code==160:
                                     
                                     print("user "+user_get.screen_name+" already friended")
                                                                  
                            else:
                                counter=counter+1
                                print("friended user "+user_get.screen_name+", friended user count="+str(counter))
                                
                    else:    
                        print("found user "+user_get.screen_name+" with "+str(user_get.followers_count)+" followers")       
                else:
                    superuser_data.append(user_get)
                    print("you will have to add superuser "+user_get.screen_name+" manually")
    print("total number of friends made is "+str(counter))

    print(superuser_data)
    print(user_failure)
    print(ss_excluded)
    print("exiting")
    return(user_data,superuser_data,user_failure,ss_excluded)

def users_unfollow(friends_names,exclude_list):
    friends_lower=[]
    for friend_name in friends_names:
        friends_lower.append('@'+friend_name.lower())
        friends_lower.append(friend_name.lower())
    
    problem_users_lower=[]
    if isinstance(exclude_list,dict):
        for problem_user in exclude_list.keys():
            problem_users_lower.append(problem_user.lower())
    else:
        for problem_user in exclude_list:
            problem_users_lower.append(problem_user.lower())
        
    final=intersection(friends_lower,problem_users_lower)
    
    for former_friend in final:
        api.destroy_friendship(former_friend)
        time.sleep(100)
        if isinstance(exclude_list,dict):
            print(former_friend+" unfollowed, reason "+exclude_list[former_friend])
        else:
            print(former_friend+" unfollowed")
    
    return(final)
    

def get_friends(user_id):
    users = []
    page_count = 0
    for user in tweepy.Cursor(api.friends, id=user_id, count=200).pages():
        page_count += 1
        print ('Getting page {} for friends'.format(page_count))
        users.extend(user)
    return users

def names_extract(user_list):
    names_list=[]
    if len(user_list)==0:
        return([])
    elif isinstance(user_list[0],twint.tweet.tweet):
        for user in user_list:
            scname=user.screen_name#TODO check how the user object works
            names_list.append(scname)

    else:
        for user in user_list:
            scname=user.screen_name
            names_list.append(scname)
    return(names_list)

def authors_extract(status_list):
    authors=[]
    if len(status_list)==0:
        return([])
    elif isinstance(status_list[0],twint.tweet.tweet):
        for status in status_list:
            authors.append(status.username)
        authors_out=set(authors)
        
   
    else:
        for status in status_list:
            authors.append(status.author.screen_name)
        authors_out=set(authors)
    return(authors_out,authors)

def post_date_list(status_list):
    
    
    date_times=[]
    if len(status_list)==0:
        return([])
    elif isinstance(status_list[0],twint.tweet.tweet):
        for status in status_list:
            date_times.append(status.datetime)
    else:
        for status in status_list:
            date_times.append(status.created_at)
    return(date_times)
      
if __name__ == '__main__':
    if load_file==False:
        list1=query_tweets(query1,option=TP)
        list2=query_tweets(query2,option=TP)
        
        list1=status_list_prune(list1)
        list2=status_list_prune(list2)
        
        status_list=list1+list2
        
        if (isinstance(status_list[0],twint.tweet.tweet)):
             for status in status_list:
                if status.username=="JackEDeakin":
                    print(status.tweet)
           
            
        else:
            for status in status_list:
                if status.author.screen_name=="JackEDeakin":
                    print(status.full_text)
    
        
        _,author_list=authors_extract(status_list)
        
        amp1=ampersant_extract(list1,option=1,trigger_length=400)
        amp2=ampersant_extract(list2,option=1,trigger_length=400)
        amp=amp1+amp2
        hash1=hash_extract(list1)
        hash2=hash_extract(list2)
        hashlist=hash1+hash2
        txt1=full_text_extract(list1)
        txt2=full_text_extract(list2)
        txt=txt1+txt2
        
        amp_sh,authors_relevant=list_cut(amp,hashlist,list(author_list),t=t,u=u)
        
        tag_posters=list(set(authors_relevant))
        
        #search through the history of the relevant authors looking for the tag:
        if TP=="tweepy":
            historic_status_list_all,text_list_all,hashtags_all,mentions_all,timestamps_all=user_history_extract(tag_posters)
            
            
            text_list=list_flat(text_list_all)
            
            amp_super=ampersant_extract(text_list,option=1,trigger_length=400)
            hash_super=hash_extract(text_list)
            #authors_super=authors_extract(text_list)
            #txt_super=
            
            amp_super_sh,_=list_cut(amp_super,hash_super,None,t=t,u=u)
            
        else:
            amp_super_sh=[]
            
        ampf=list_flat(amp_sh+amp_super_sh)
        amp_dict=list_freq(ampf)
        
        keylist=list(amp_dict.keys())
        A=api.me()
        user_id=A.id
        friends_objects=get_friends(user_id=user_id)
        
        friends_names=names_extract(friends_objects)
        
        #export to csv
        patel1.save_json(amp_sh,save_dir+"raw_ss_tweets.json")
        list_write(save_dir+"friendlist.csv",friends_names)
        if os.path.exists(save_dir+"socialist_sunday_list.csv"):
            os.rename(src=save_dir+"socialist_sunday_list.csv",dst=save_dir+"socialist_sunday_list_old.csv")
        list_write(save_dir+"socialist_sunday_list.csv",keylist) 
    #while(1):
        #myfriends=api.friends()
        #for i in range(len(myfriends)):
            #friends_names.append(myfriends[i].screen_name)
            
     #   print("added "+str(len(myfriends))+" friends")
    else:
        friends_names=list_flat(array_load(save_dir+"friendlist.csv"))
        keylist=list_flat(array_load(save_dir+"socialist_sunday_list.csv"))
        
    if random_shuffle:
        random.shuffle(keylist)
        
    user_data,superuser_data,user_failure,ss_excluded=users_follow(keylist,friends_names,max_follower_count,follow,lookup)
    superusers=[user.screen_name for user in superuser_data]
    list_write(save_dir+"socialist_sunday_list_superusers.csv",superusers)
    
    A=api.me()
    user_id=A.id
    friends_objects=get_friends(user_id=user_id)
    
    friends_names=names_extract(friends_objects)
    list_write(save_dir+"friendlist.csv",friends_names)

    #unfollow any problem users
    unfollowed=users_unfollow(friends_names,exclude_list)
#%%      
    #stats
    status_list=list1+list2
    P=post_date_list(status_list)
    
  
    
    #shared followers
    
    #extract followers of problem users
    #see how many are SS regulars
    dotdotdot="\u2026"    
    keylist_0=array_load(save_dir+"socialist_sunday_list.csv")
    keylist_1=[key[0] for key in keylist_0]
    keylist_2=[key for key in keylist_1 if not key.endswith(dotdotdot)]
    keylist_3=list(set([key for key in keylist_2 if not key.endswith(":")]))
    
    
    keylist=keylist_3
    bad_words=["Soros","Rothschild","Zio","soros","rothschild","zio","Rotschild","rotschild","Cabal","holohoax","Holohoax","Jewish money", "jewish money", "Jewish influence","jewish influence","ZioNazi","Khazar","Khazarian","NWO"]

    
    data_dump=save_dir+"total_tweets_dump.json"
    id_list_all,text_list_all,hashtags_all,mentions_all,timestamps_all=user_history_extract(keylist,data_dump,option=TP,query=bad_words)
    
    
    #save the text
    import csv
    with open("ss_text_dump.csv","w",newline="") as f:
        writer=csv.writer(f)
        for count,text in enumerate(text_list_all):
            writer.writerows(map(lambda x: [x], id_list_all[count]))
            for tweet in text:
                writer.writerows(tweet)
    
    
    if TP=="tweepy":    
        #first check for bad words among the authors:
        for count, denizen in enumerate(keylist):
    
            for count2, text in enumerate(text_list_all[count]):
                tokens=text.split()
                for bad_word in bad_words:
                    if bad_word in tokens:
                        id_curr=id_list_all[count][count2]
                        print(denizen)
                        print(text)
                        list_append(filepath=save_dir+"socialist_sunday_badboys.csv",the_list=[id_curr])
        
        
    
    if wainwright_import:    
        problem_users=hashtags[0:227]
        
        friends_lower=[]
        for friend_name in friends_names:
            friends_lower.append(friend_name.lower())
        
        
        problem_users_lower=[]
        for problem_user in problem_users:
            problem_users_lower.append(problem_user.lower())
        
        final=intersection(friends_lower,problem_users_lower)
        list_write(save_dir+"problem_users_socialist_sunday.csv",problem_users_lower)    
        
        keylist_l=[]
        for key in keylist:
            keylist.append(key.lower())
        
        
        
            
    #print(amp_dict)
    
    #date range
    
    
#    #check in case of stray extras:
#    u_check="@AndJeremySaid"
#    for count, entry in enumerate(amp1):
#        #print(len(list1[count].full_text))
#        if (u_check in entry):
#            print(entry)
#            #print(list1[count])
#
#            special=list1[count]
#            print(count)
#            print(special.author.name)
#            print(special.full_text)    
#    for count, entry in enumerate(amp2):
#        #print(len(list2[count].full_text))
#        if (u_check in entry):
#            print(count)
#            print(entry)
#            #print(list2[count])
#            special=list2[count]
#            print(special.full_text)
#            print(special.author.name)   
#    
#    
#    for count, entry in enumerate(amp1):
#        #print(len(list1[count].full_text))
#        if (len(list1[count].full_text)>500):
#            print(entry)
#            #print(list1[count])
#
#            special=list1[count]
#            print(special.author.name)
#            print(special.full_text)
#    for count, entry in enumerate(amp2):
#        #print(len(list2[count].full_text))
#        if (len(list2[count].full_text)>500):
#            print(entry)
#            #print(list2[count])
#            special=list2[count]
#            print(special.full_text)
#            print(special.author.name)
            
            


