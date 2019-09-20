#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 11 02:37:36 2019

@author: deepthought42
"""

import bokeh

from twitter_orig_utils import *
import patel1
from bokeh.plotting import figure
from bokeh.io import show, output_notebook
import numpy as np
import pandas as pd
import pylab as pl

def creation_histogram(user_objects,filename):
    
    _,h_set,f_set=patel1.attr_dict_create(user_objects,filename)    
    
    create_hist(h_set,title='Weeks since account creation',xlab='no weeks',ylab='frequency',range0=0,range1=700,xticks_per_bar=10)
    
    create_hist(f_set,title="Follower numbers",xlab='no. followers',ylab='frequency',range0=0,range1=max(non_zero_entries(f_set)))
    
    create_truncated_hist(f_set,title="Follower numbers",xlab='no. followers',ylab='frequency',percent=5,range0=0,range1=max(non_zero_entries(f_set)))
    
    return h_set,f_set

def create_hist(data,title,xlab,ylab,range0=0,range1=100,xticks_per_bar=10):
    
    arr_hist, edges = np.histogram(vec_freq_convert(data), 
                               bins = int((range1-range0)/xticks_per_bar), 
                               range = [range0, range1])
    
    delays = pd.DataFrame({'arr_delay': arr_hist, 
                       'left': edges[:-1], 
                       'right': edges[1:]})
    
    p = figure(plot_height = 600, plot_width = 600, 
           title = title,
           x_axis_label = xlab, 
           y_axis_label = ylab)

    # Add a quad glyph
    p.quad(bottom=0, top=delays['arr_delay'], 
       left=delays['left'], right=delays['right'], 
       fill_color='red', line_color='black')
    
    
    show(p)
    
def create_truncated_hist(data,title,xlab,ylab,percent=10,range0=0,range1=100,xticks_per_bar=10):
    T=data_trim(vec_freq_convert(data),percent)
    range1=max(T)
    
    arr_hist, edges = np.histogram(T, 
                               bins = int((range1-range0)/xticks_per_bar), 
                               range = [range0, range1])
    
    delays = pd.DataFrame({'arr_delay': arr_hist, 
                       'left': edges[:-1], 
                       'right': edges[1:]})
    
    p = figure(plot_height = 600, plot_width = 600, 
           title = title,
           x_axis_label = xlab, 
           y_axis_label = ylab)

    # Add a quad glyph
    p.quad(bottom=0, top=delays['arr_delay'], 
       left=delays['left'], right=delays['right'], 
       fill_color='red', line_color='black')
    
    
    show(p)    


def create_log_hist(data,title,xlab,ylab,range0=1,range1=1000000,xticks_per_bar=10):
    pl.hist(vec_freq_convert(data), bins=np.logspace(np.log10(range0),np.log10(range1), 500))
    pl.gca().set_xscale("log")
    pl.show()
    
    