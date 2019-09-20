#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 03:09:46 2019

@author: deepthought42
"""



#list ops
from collections import Sequence
from itertools import chain, count
import pandas as pd
import numpy as np
import os
import time

def list_depth(seq):
    
    
    seq = iter(seq)
    try:
        for level in count():
            print(level)
            seq = chain([next(seq)], seq)
            seq = chain.from_iterable(s for s in seq if isinstance(s, Sequence))
    except StopIteration:
        print("")
        return level

def depth(arg, exclude=None):
    if exclude is None:
        exclude = (str, )

    if isinstance(arg, tuple(exclude)):
        return 0

    try:
        if next(iter(arg)) is arg:  # avoid infinite loops
            return 1
    except TypeError:
        return 0

    try:
        depths_in = map(lambda x: depth(x, exclude), arg.values())
    except AttributeError:
        try:
            depths_in = map(lambda x: depth(x, exclude), arg)
        except TypeError:
            return 0

    try:
        depth_in = max(depths_in)
    except ValueError:
        depth_in = 0

    return 1 + depth_in

def list_write(filepath,the_list,replace=True):
    print(filepath)
    if os.path.isfile(filepath):
        filepath_tok=filepath.split(".")
        filepath_new=filepath_tok[0]+str(time.time())+filepath_tok[1]
        os.rename(filepath,filepath_new)
    with open(filepath, 'w') as file_handler:
        #print("A")
        for item in the_list:
            if isinstance(item, str):
                file_handler.write("{}\n".format(item))
            else:
                for j in range(len(item)):
                    file_handler.write("{}".format(item[j]))
                    if (j+1)<len(item):
                        file_handler.write("\t")
                    else:
                        file_handler.write("\n")
                        
def list_append(filepath,the_list):
    print(filepath)
    with open(filepath, 'a') as file_handler:
        #print("A")
        for item in the_list:
            if isinstance(item, str):
                #print("here")
                file_handler.write("{}\n".format(item))
            elif isinstance(item, int):
                #print("here")
                file_handler.write("{}\n".format(item))  
            else:
                for j in range(len(item)):
                    file_handler.write("{}".format(item[j]))
                    if (j+1)<len(item):
                        file_handler.write("\t")
                    else:
                        file_handler.write("\n")
                        
def lists_combine_col(list1,list2):
    combined=[]
    l=min(len(list1),len(list2))
    for i in range(l):
        pair=[list1[i],list2[i]]
        combined.append(pair)
    return combined
#flattens a nested list
def list_flat(a):
    #return functools.reduce(operator.iconcat, a, [])
    return [item for sublist in a for item in sublist]

#flattens a list, removes duplicates and missing values
def list_prune(list1):
    list4=[]
    list2=list_flat(list1)
    try:
        list3=list(set(list2))
    except TypeError:
        for value in list2:
            if value!='nan':
                if value not in list4:
                    list4.append(value)
                    
            
    else:
        for entry in list3:
            if not entry=='nan':
                list4.append(entry)
    return(list4)
    
#dict methods
def keywithmaxval(d):
     """ a) create a list of the dict's keys and values; 
         b) return the key with the max value"""  
     v=list(d.values())
     k=list(d.keys())
     return k[v.index(max(v))]

#list intersection
def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3 


#Save/load
    
    #loader
def array_load(filepath):
    A=pd.read_csv(filepath,sep="\t",keep_default_na=False)
    return A.values

def vec_freq_convert(h_set):
    freq=np.repeat(range(len(h_set)),h_set)
    return freq

def non_zero_entries(L):
     ls = [i for i, e in enumerate(L) if e != 0]
     return ls
 
def data_trim(data,percent=0.1):
    sorted_data = sorted(data)
    n = len(sorted_data)
    outliers = n*percent/100 #may want some rounding logic if n is small
    trimmed_data = sorted_data[round(outliers): round(n-outliers)]
    return(trimmed_data)