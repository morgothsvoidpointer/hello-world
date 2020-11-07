# -*- coding: utf-8 -*-

"""
This script goes through the list of people you follow and removes anyone who doesn't follow you.

The lists special_users, special_orgs and special_peeps allow you to specify people you wish to follow even though they do not reciprocate.

Because the other script never friends people with more than max_follower_count followers, this one won't remove such people - since you never added them.

"""


#import SocialistSunday
import add_by_tag
import tweepy
import os
from twitter_orig_utils import *
from twitter_authorise import api, auth, save_dir, userhome, python_dir

#users not to touch:

special_users=["OwenJones84","paulmasonnews","graceblakeley","AnnPettifor","JacDunc1","Alston_UNSR","JamesEFoster","sylviatopp","nbissell","jennirsl","_jamesmeek","shoshanazuboff","Tom_deWaal","LaurenceBroers","katypearce","aniboghoss"]

special_orgs=["NHSMillion","LabourList","tribunemagazine","LeftieStats","ByDonkeys","Orwell_Society","RightWingWatch"]

special_peeps=['ischlackow','M_dreiviertel','arojomaths','MiglioMat']


#users above this no. of followers won't be unfridended
max_follower_count2=10000


 
special_users.extend(special_orgs)

special_users.extend(special_peeps)



def get_follower_list(username):
    follower_list=[]
    for users in tweepy.Cursor(api.followers, screen_name=username, count=200).pages():
        for user in users:
            follower_list.append(user.screen_name)
            print(user.screen_name)
            print(len(follower_list))
    return(follower_list)

def get_friend_list(username):
    friend_list=[]
    for users in tweepy.Cursor(api.friends, screen_name=username, count=200).pages():
        for user in users:
            friend_list.append(user.screen_name)
            print(user.screen_name)
            print(len(friend_list))
    return(friend_list)

#%%    
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
    
    if os.path.exists(save_dir+"socialist_sunday_list_superusers.csv"):
        superusers=list_flat(array_load(save_dir+"socialist_sunday_list_superusers.csv"))
    
    for bad_friend in bad_friends:
        if '@'+bad_friend in keylist:
            if not os.path.exists(save_dir+"socialist_sunday_list_superusers.csv"):
                try:
                    user_get=api.get_user(screen_name=bad_friend)
                except tweepy.TweepError:
                    print("user "+bad_friend+" threw error")
                    continue
                if user_get.followers_count<max_follower_count2 and user_get.verified==False:
                    very_bad_friends.append(bad_friend)
            else:
                if bad_friend not in superusers:
                    very_bad_friends.append(bad_friend)
    
    #remove special users
    
    small_bad_friends=[]
    for bad_friend in bad_friends:
        if bad_friend not in special_users:
            small_bad_friends.append(bad_friend)
           
    list_write(save_dir+"very_bad_friends.csv",small_bad_friends)
#%% 
    import py_compile 
    py_compile.compile('add_by_tag.py')
    from add_by_tag import *
    #now unfollow
    final=users_unfollow(Friends,small_bad_friends)
