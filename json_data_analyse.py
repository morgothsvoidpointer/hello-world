#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 20:22:58 2019

@author: deepthought42
"""

import sys
import os
from twitter_orig_utils import *
try:
    from twitter_orig import python_dir, save_dir
except ImportError:
    userhome = os.path.expanduser('~')
    #python_dir=userhome+'/Documents/ThinkTank/library/python/python_other/word_match/'
    python_dir=userhome+'/Documents/word_files_dir/'
    save_dir=python_dir+'Output/'
    if python_dir not in sys.path: sys.path.append(python_dir)

from SingleUserExtract import user_history_extract
import patel1

import np
import time
import tweepy
import twint
import re
import asyncio
import io
import json


import bigjson
keywords=["Soros","Rothschild","Zio","soros","rothschild","zio","Rotschild","rotschild","Cabal","holohoax","Holohoax","Jewish money", "jewish money", "Jewish influence","jewish influence","ZioNazi","Khazar","Khazarian","NWO"]

def bigjson_read(filename,fun):
        
    with open(filename, 'r',encoding="utf-16") as f:
        j = bigjson.load(f)
        k=0
        while(1):
            try:
                element=j[k]
            except EOFError:
                return
            else:
                fun(element)
                k=k+1

def bigjson_test(filename):
    with open(filename, 'rb') as f:
        
        for k in range(100):
            j = bigjson.load(f)
            element=j
            print(element)
        
        
def read_by_line(filename):
    with open(filename, 'r',encoding="ascii") as f:
        for i in range(10):
            f.readline()
          
def keywords_check(element,bad_words=keywords):

    if isinstance(element,dict):

        try:
            text=element["full_text"]
        except KeyError:
            text=element["text"]
        tokens=text.split()
        for bad_word in bad_words:
            if bad_word in tokens:
                id_curr=element["id"]
                denizen=element["user"]["screen_name"]
                crimetime=element["created_at"]
                print(denizen)
                print(text)
                list_append(filepath=save_dir+"socialist_sunday_badboys.csv",the_list=[denizen+" "+crimetime+" "+text+" "+str(id_curr)])

def append_repair(filename,fun):
     element_count=0
     line_count=0
     with io.open(filename, "r", encoding="utf-8") as f:
         g=io.open(save_dir+"temp.json","w",encoding="utf-8")
         for s in f:
             line_count+=1
             if "][" in s and "\"" not in s:
                 #print(s)
                 g.write("]")
                 g.close()
                 g=io.open(save_dir+"temp.json","r",encoding="utf-8")
                 try:
                     P=json.load(g)
                     print(P[0]["user"]["screen_name"]+" "+str(len(P)))
                 except json.JSONDecodeError:
                     print("json error")
                     #return element_count
                 for element in P:
                     ret=fun(element)
                 
                 g.close()
                 os.remove(save_dir+"temp.json")
                 g=io.open(save_dir+"temp.json","w",encoding="utf-8")
                 g.write("[")
                 element_count+=1
             
                 
             else:
                 g.write(s)
         g.close()
         g=io.open(save_dir+"temp.json","r",encoding="utf-8")
         try:
             P=json.load(g)
             print(P[0]["user"]["screen_name"]+" "+str(len(P)))
         except json.JSONDecodeError:
             print("json error")
             #return element_count
         for element in P:
             ret=fun(element)
         
         g.close()
         
         print(element_count)
     return element_count
 
def jsonl_to_json(filename):
    import json_lines
    status_list=[]
    with open(filename, 'rb') as f: # opening file in binary(rb) mode    
       for item in json_lines.reader(f):
           status_list.append(item)
    return(status_list)


def folder_analyse(folder_name,keywords,k_print):
    filelist=os.listdir(folder_path)
    K=[0]*len(keywords)#counters list
    I=[0]*len(filelist)#users list
    printed_count=0
    for count,file in enumerate(filelist):
        indic_P=0
        I[count]=[0]*len(keywords)
        try:
            J=json.loads(folder_path+filelist[count])
        except json.JSONDecodeError:
            try:
                J=jsonl_to_json(folder_path+filelist[count])
            except json.JSONDecodeError:
                print("giving up on file "+file)
        for count2,key in enumerate(keywords):
            indic_K=0
            for status in J:
                if " " not in key:
                    text=status["tweet"]
                    regex = r'\b\w+\b'
                    tok=re.findall(regex,text)
                else:
                    tok=status["tweet"]
                if key in tok:
                    indic_K=1
                    I[count][count2]=I[count][count2]+1
                    
                    if key in k_print:
                        print(status["date"])
                        print(status["username"])
                        print(status["tweet"])
                        indic_P=1
            K[count2]=K[count2]+indic_K
        printed_count=printed_count+indic_P
    print(np.column_stack([keywords,K]))
    return(K,I,printed_count)                 
        
if __name__ == '__main__':

    option="folder"
    
    if option=="single file":        
        filename=save_dir+"total_tweets_dump.json"
        
        e=append_repair(filename,keywords)
    elif option=="folder":
        folder_path=save_dir+"users_ss/"

        filelist=os.listdir(folder_path)
        i=654
        try:
            J=json.loads(folder_path+filelist[i])
        except json.JSONDecodeError:
            J=jsonl_to_json(folder_path+filelist[i])

            
            
        
        for entry in J:
            print(entry["name"])
            print(entry["tweet"])
        
        
        k_print="holohoax"
        
        kw_exclude={} #for each keyword, words that are also presont that 'exonerate'
        kw_include={} #conversely, words that 'condemn'
        K,I,p=folder_analyse(folder_path,keywords,k_print)

        #import and check wainwright's lot:
        
        wainwright_list=array_load(save_dir+"problem_users_socialist_sunday.csv")
        w_list=[entry[0] for entry in wainwright_list]
        our_list=[filename.split("_")[0] for filename in filelist]
        
        
        inters=list(set(our_list) & set(w_list))
            
        
        
        
        
        
        
        
        
        
        
        