#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 10:15:51 2019

@author: deepthought42
"""

from tweepy import OAuthHandler
from tweepy import API
from collections import Counter
from datetime import datetime, date, time, timedelta
import twint
import sys
import json
import os
import io
import re
import time
 
from twitter_authorise import api, auth, save_dir, userhome, python_dir

auth_api=auth


# Helper functions to load and save intermediate steps - TODO later add a custom Munch option
def save_json(variable, filename):
    with io.open(filename, "w", encoding="utf-8") as f:
        try:
            f.write(str(json.dumps(variable, indent=4, ensure_ascii=False)))
        except TypeError:
            if isinstance(variable,list):
                variable_j=[None]*len(variable)
                for count,entry in enumerate(variable):
                    if isinstance(variable[count],dict):
                        variable_j[count]=json.loads(entry.toJSON())
                    else:
                        variable_j[count]=variable[count]._json
                        
                        
            f.write(str(json.dumps(variable_j, indent=4, ensure_ascii=False)))
                        
def append_json(variable, filename):
    with io.open(filename, "a", encoding="utf-8") as f:
        try:
            f.write(str(json.dumps(variable, indent=4, ensure_ascii=False)))
        except TypeError:
            if isinstance(variable,list):
                variable_j=[None]*len(variable)
                for count,entry in enumerate(variable):
                    if isinstance(variable[count],dict):
                        variable_j[count]=json.loads(entry.toJSON())
                    elif isinstance(variable[count],twint.tweet.tweet):
                        variable_j[count]=json.loads(entry)                        
                    else:
                        variable_j[count]=variable[count]._json
                        
                        
            f.write(str(json.dumps(variable_j, indent=4, ensure_ascii=False)))

                
def load_json(filename):
    ret = None
    if os.path.exists(filename):
        try:
            with io.open(filename, "r", encoding="utf-8") as f:
                ret = json.load(f)
        except:
            pass
    return ret

#def loads_json(filename):
#    rets=load_json(filename)
#    ret=[]
#    for item in rets:
#        ret.append(json.loads(item))
#
#    return ret
 
def try_load_or_process(filename, processor_fn, function_arg):
    load_fn = None
    save_fn = None
    if filename.endswith("json"):
        load_fn = load_json
        save_fn = save_json
    else:
        load_fn = load_bin
        save_fn = save_bin
    if os.path.exists(filename):
        print("Loading " + filename)
        return load_fn(filename)
    else:
        ret = processor_fn(function_arg)
        print("Saving " + filename)
        save_fn(ret, filename)
        return ret
 
# Some helper functions to convert between different time formats and perform date calculations
def twitter_time_to_object(time_string):
    twitter_format = "%a %b %d %H:%M:%S %Y"
    match_expression = "^(.+)\s(\+[0-9][0-9][0-9][0-9])\s([0-9][0-9][0-9][0-9])$"
    match = re.search(match_expression, time_string)
    if match is not None:
        first_bit = match.group(1)
        second_bit = match.group(2)
        last_bit = match.group(3)
        new_string = first_bit + " " + last_bit
        date_object = datetime.strptime(new_string, twitter_format)
        return date_object
 
def time_object_to_unix(time_object):
    return int(time_object.strftime("%s"))
 
def twitter_time_to_unix(time_string):
    return time_object_to_unix(twitter_time_to_object(time_string))
 
def seconds_since_twitter_time(time_string):
    input_time_unix = int(twitter_time_to_unix(time_string))
    current_time_unix = int(get_utc_unix_time())
    return current_time_unix - input_time_unix
 
def get_utc_unix_time():
    dts = datetime.utcnow()
    return time.mktime(dts.timetuple())
 
# Get a list of follower ids for the target account
def get_follower_ids(target):
    return auth_api.followers_ids(target)
 
# Twitter API allows us to batch query 100 accounts at a time
# So we'll create batches of 100 follower ids and gather Twitter User objects for each batch
def get_user_objects(follower_ids):
    batch_len = 100
    num_batches = len(follower_ids) / 100
    batches = (follower_ids[i:i+batch_len] for i in range(0, len(follower_ids), batch_len))
    all_data = []
    for batch_count, batch in enumerate(batches):
        sys.stdout.write("\r")
        sys.stdout.flush()
        sys.stdout.write("Fetching batch: " + str(batch_count) + "/" + str(num_batches))
        sys.stdout.flush()
        users_list = auth_api.lookup_users(user_ids=batch)
        users_json = (map(lambda t: t._json, users_list))
        all_data += users_json
    return all_data
 
# Creates one week length ranges and finds items that fit into those range boundaries
def make_ranges(user_data, num_ranges=750):
    range_max = 604800 * num_ranges
    range_step = range_max/num_ranges
 
# We create ranges and labels first and then iterate these when going through the whole list
# of user data, to speed things up
    ranges = {}
    labels = {}
    for x in range(num_ranges):
        start_range = x * range_step
        end_range = x * range_step + range_step
        label = "%03d" % x + " - " + "%03d" % (x+1) + " weeks"
        labels[label] = []
        ranges[label] = {}
        ranges[label]["start"] = start_range
        ranges[label]["end"] = end_range
    for user in user_data:
        if "created_at" in user:
            account_age = seconds_since_twitter_time(user["created_at"])
            for label, timestamps in ranges.items():
                if account_age > timestamps["start"] and account_age < timestamps["end"]:
                    entry = {} 
                    id_str = user["id_str"] 
                    entry[id_str] = {} 
                    fields = ["screen_name", "name", "created_at", "friends_count", "followers_count", "favourites_count", "statuses_count"] 
                    for f in fields: 
                        if f in user: 
                            entry[id_str][f] = user[f] 
                    labels[label].append(entry) 
    return labels

def attr_dict_create(user_objects,filename="ranges.json"):


    total_objects = len(user_objects)
    
    
    
# Record a few details about each account that falls between specified age ranges
    ranges = make_ranges(user_objects)
    save_json(ranges, filename)
 
# Print a few summaries
    summary_creation=[0]*len(ranges)
    summary_followers=[0]*10000000
    
    print
    print("\t\tFollower age ranges")
    print("\t\t===================")
    total = 0
    following_counter = Counter()
    extra_counter=0
    for label, entries in sorted(ranges.items()):
        print("\t\t" + str(len(entries)) + " accounts were created within " + label)
        summary_creation[extra_counter]=len(entries)
        total += len(entries)
        for entry in entries:
            for id_str, values in entry.items():
                if "friends_count" in values:
                    following_counter[values["friends_count"]] += 1
        extra_counter += 1        
        
    print("\t\tTotal: " + str(total) + "/" + str(total_objects))
    print
    print("\t\tMost common friends counts")
    print("\t\t==========================")
    total = 0
    for num, count in following_counter.most_common(2000):
        total += count
        print("\t\t" + str(count) + " accounts are following " + str(num) + " accounts")
        summary_followers[num]=count
    print("\t\tTotal: " + str(total) + "/" + str(total_objects))
    print
    print
        
    
    
    return ranges,summary_creation,summary_followers

if __name__ == "__main__": 
    account_list = ["CaraPac46808618"]
    if (len(sys.argv) > 1):
        account_list = sys.argv[1:]
 
    if len(account_list) < 1:
        print("No parameters supplied. Exiting.")
        sys.exit(0)
 

 
    for target in account_list:
        print("Processing target: " + target)
 
# Get a list of Twitter ids for followers of target account and save it
        filename = target + "_follower_ids.json"
        follower_ids = try_load_or_process(filename, get_follower_ids, target)
 
# Fetch Twitter User objects from each Twitter id found and save the data
        filename = target + "_followers.json"
        user_objects = try_load_or_process(filename, get_user_objects, follower_ids)
        total_objects = len(user_objects)
 
# Record a few details about each account that falls between specified age ranges
        ranges = make_ranges(user_objects)
        filename = target + "_ranges.json"
        save_json(ranges, filename)
 
# Print a few summaries
        print
        print("\t\tFollower age ranges")
        print("\t\t===================")
        total = 0
        following_counter = Counter()
        for label, entries in sorted(ranges.items()):
            print("\t\t" + str(len(entries)) + " accounts were created within " + label)
            total += len(entries)
            for entry in entries:
                for id_str, values in entry.items():
                    if "friends_count" in values:
                        following_counter[values["friends_count"]] += 1
        print("\t\tTotal: " + str(total) + "/" + str(total_objects))
        print
        print("\t\tMost common friends counts")
        print("\t\t==========================")
        total = 0
        for num, count in following_counter.most_common(2000):
            total += count
            print("\t\t" + str(count) + " accounts are following " + str(num) + " accounts")
        print("\t\tTotal: " + str(total) + "/" + str(total_objects))
        print
        print