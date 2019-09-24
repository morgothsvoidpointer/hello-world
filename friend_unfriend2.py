# -*- coding: utf-8 -*-
"""
Редактор Spyder

Это временный скриптовый файл.
"""

#
import SocialistSunday
import tweepy
import twitter_orig_utils


consumer_key = 'Xa8XbijTP7F3sg0QJ1QUoLq6f'
consumer_secret = 'cRBjxlQK3PO2cy4zFnfZGlLdtIYm1c9KMIe8IsZVaE0OqFIMsh'
access_token = '1092850952284131328-6prMHiiBPsQHU5In4xho9N1cQy9wpO'
access_token_secret = 'BOs3QPs7PnF8uRMgaexuv3BizPPkMeSdXq3YEqATcIsM9'

query1="#SocialistSunday -filter:retweets"
query2="#SocialistAnyDay -filter:retweets"



# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
 
# Creation of the actual interface, using authentication
api = tweepy.API(auth,wait_on_rate_limit=True) 

def get_follower_list(username):
    follower_list=[]
    for user in tweepy.Cursor(api.followers, screen_name=username, count=200).items():
        follower_list.append(user.screen_name)
        print(user.screen_name)
        print(len(follower_list))
    return(follower_list)

def get_friend_list(username):
    friend_list=[]
    for user in tweepy.Cursor(api.friends, screen_name=username, count=200).items():
        friend_list.append(user.screen_name)
        print(user.screen_name)
        print(len(friend_list))
    return(friend_list)    

    
#now unfollow people I follow who don't follow me, belong to the SS-list and don't have above a set number of friends.
    
if __name__ == '__main__':
    username="@carapac46808618"
    
    #fetch friends
    Friends=get_friend_list(username)
    Followers=get_follower_list(username)
    
    bad_friends=[]
    for friend in Friends:
        if friend not in Followers:
            bad_friends.append(friend)
            
            
    list_write(save_dir+"bad_friends.csv",bad_friends)
            
    #intersect bad friends with social sunday list
    keylist=list_flat(array_load(save_dir+"socialist_sunday_list_old.csv"))
    very_bad_friends=[]
    for bad_friend in bad_friends:
        if bad_friend in keylist:
            very_bad_friends.append(bad_friend)
    
    
    #exclude people with too many followers
            
    #already done

    #now unfollow
    final=SocialistSunday.user_unfollow(Friends,very_bad_friends)
    

        
            
            