#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 22:54:58 2019

@author: deepthought42
"""

import nltk
nltk.download('punkt')
from textblob import TextBlob

def bigrams_adj_clean(bigrams):
    cleaned_list=[]
    for bigram in bigrams:
        if "" in bigram:
            continue
        
        speech_parts=nltk.pos_tag(bigram)
        if speech_parts[-1][1]=='JJ':
            print(speech_parts)
        elif speech_parts[-1][1] in ['TO','IN','AT','DT','CC']:
            print(speech_parts)
        else:
            cleaned_list.append(bigram)
    return cleaned_list


def part_add(frequencies):
    F=frequencies
    for i in range(len(F)):
        word=F[i][0]
        if word[:-1]=='@':
            word=word[:-1]
        if " " in word:
            part=(word, "PST")
        else:
            part=nltk.pos_tag([word])
        F[i]=list(F[i])+list([part[0][1]])
    return F
    



def plural_to_singular(plurals):
    blob = TextBlob(plurals)
    singles = [word.singularize() for word in blob.words]
    return singles