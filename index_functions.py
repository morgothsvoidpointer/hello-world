import numpy as np
from collections import Iterable
import json
import copy
import nltk_functions
 
def flatten(items):
    """Yield items from any nested iterable; see Reference."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in flatten(x):
                yield sub_x
        else:
            yield x
            
def list_to_string(lst):
    out_string=" ".join(lst)
    return(out_string)
    

#this function determines the location of the submitted token in the data\
#input is a 'tokenized' list of lists\
#output is the location\
def query_locate(data,query):
  locations=[]
  for i in range(len(data)):
    locations.append([])
    para=data[i]
    for j in range(len(para)):
      token=para[j]
      if token==query:
        locations[i].append(j)
      #add any 'mutations' of the token during cleaning.\
      if token==query+".":
        locations[i].append(j)
      if token==query+":":
        locations[i].append(j)
      if token==query+"@":
        locations[i].append(j)
  return(locations)
        
 #this function takes in a query word and scans the text for all bigrams involving it\
def text_scan(data,query,stopwords):

  locations=query_locate(data,query)
 
  forward_bigrams=[]
  backward_bigrams=[]
  # print(locations)
  for i in range(len(locations)):
    if (len(locations[i])>0):
      #print(i)
      for j in locations[i]:
        if j>0:
          gram=[data[i][j-1],data[i][j]]
          if data[i][j-1] in stopwords and j>1:
              gram=[data[i][j-2]]+gram
              if data[i][j-2] in stopwords and j>2:
                  gram=[data[i][j-3]]+gram
          if '@' in gram[-1] and j<len(data[i])-1:
              gram.append(data[i][j+1])
          backward_bigrams.append(gram)
        de=(len(data[i])-1)
        if j<de: 
          gram1=[data[i][j],data[i][j+1]]
          if data[i][j+1] in stopwords and j<de-1:
              gram1.append(data[i][j+2])
              if data[i][j+2] in stopwords and j<de-2:
                  gram1.append(data[i][j+3])
          if '@' in gram1[-1] and j<de-3:
              gram1.append(data[i][j+4])
          forward_bigrams.append(gram1)
                  
          
  
  #check for stopwords, add previous/next word if stopword
  
  
  #count up the unique 2-grams\
  bigrams=forward_bigrams+backward_bigrams
 
  #btup=[tuple(t) for t in bigrams]
 
  #bset=set(btup)
 
  #unique_bigrams=[list(t) for t in bset]
  #print(bigrams)
  #print(type(bigrams))
  #print(bigrams)
  bigrams=bigrams_prune(bigrams)
  if len(bigrams)>1:
  #print(type(bigrams))
      try:
          unique_bigrams,counts=np.unique(bigrams,return_counts=True,axis=0)
      except TypeError:
          unique_bigrams,counts=np.unique(bigrams,return_counts=True)
      unique_bigrams=unique_bigrams.tolist()
      counts=counts.tolist()
  elif len(bigrams)==1:
      unique_bigrams=bigrams
      counts=[1]
  elif len(bigrams)==0:
      unique_bigrams=[]
      counts=[]
  
  #print(unique_bigrams)
  return(locations,forward_bigrams,backward_bigrams,unique_bigrams,counts)

def bigrams_prune(bigrams):
    bigrams_pruned=[]
    for bigram in bigrams:
        #print(bigram)
        
        
        
        rem=0
        for i in range(len(bigram)-1):
            if bigram[i][-1]=='.':
                rem=1
            if bigram[i][-1]==':':
                rem=1            
        end_bigram=bigram[-1]
        if end_bigram[-1]=='.':
            bigram[-1]=bigram[-1][:-1]

        if end_bigram[-1]==':':
            bigram[-1]=bigram[-1][:-1]       
            
        if rem==0:
            bigrams_pruned.append(bigram)
    return bigrams_pruned

 
def bigrams_find(frequencies,data,all_stopwords,fr_limit=0):
    bigrams=[]
    counts_list=[]
    Fdata=list(flatten(data))
    for i in range(len(frequencies)):
        if frequencies[i][1]<fr_limit:
            next
        word=frequencies[i][0]
        if word in Fdata:
            _,_,_,unique_bigrams,counts=text_scan(data,word,all_stopwords)
            bigrams.append(unique_bigrams)
            counts_list.append(counts)
    return(bigrams,counts_list)
        
        
        
#def pagination(text,num_lines_per_page=50):
     

def stop_search(sentence,stopwords,start_pt,direction,caps_only):
    l=len(sentence)
    if direction==1:
        out=[]
        i=1
        if (start_pt+1<l):
            out.append(sentence[start_pt+i])
        while start_pt+i<l-1 and sentence[start_pt+i] in stopwords:
            i=i+1
            out.append(sentence[start_pt+i])
        return out
    if direction==-1:
        out=[]
        i=1
        if (start_pt>0):
            out.append(sentence[start_pt-i])
        while start_pt-i>0 and (sentence[start_pt-i] in stopwords or len(sentence[start_pt-i])==2):
            i=i+1
            out.append(sentence[start_pt-i])
        out.reverse()
        return out 
        

#def caps_combine(pronouns,tokens,stopwords,caps_only,frequencies_single):

            #now go back and delete unpopular entries...
            



           

#check if list2 is a consecutive sublist of list1
def sublist_consec(list1,list2):
    l1=copy.deepcopy(list1)
    l2=copy.deepcopy(list2)
    l1=sentence_quick_clean(l1)
    l2=sentence_quick_clean(l2)   
    l=len(l2)
    m=len(l1)
    if l>m:
        return False
    else:
        for k in range(m-l):
            if l2==l1[k:(k+l)]:

                return (k+1)
    return False
        
def sentence_quick_clean(sentence):
   for count, words in enumerate(sentence):
        words=words.replace(",","")
        words=words.replace(".","")             
        words=words.replace(":","")
        words=words.replace("@","")
        sentence[count]=words
   return sentence
                    
def multiplicities_extract(S):
   F=[]
   for i in range(len(S)):    
        F.append([])
        if len(S[i])==0:
            continue
        try:
            U=np.unique(S[i],return_counts=True,axis=0)
            if isinstance(U,tuple):
                U=list(U)
            for k in range(len(U)):
                Z=U[k].tolist()
                U[k]=Z
        except TypeError:
            U=np.unique(S[i],return_counts=True)
        if len(S[i])==1:
            F[i].append([S[i][0],1])
        elif len(U[0])==1:
            F[i].append([U[0][0],len(S[i])])
        else:
            for j in range(len(U[0])):
                F[i].append([U[0][j],U[1][j]])
   
            
   return(F)    
        
 

def quote_det(s,start="‘",stop="’"):
    t=""
    count=-1
    for i in range(len(s)):
        if s[i]==start:
            count=1

        elif s[i]==stop and count==1:
            if i==(len(s)-1):
                count=0

            elif s[i+1]==" ":
                count=0

            elif i>0 and s[i-1]=="s":
                print("Warning: could be a hidden apostrophe")
#                print(s[(max(0,s-10):min(len(s)-1,s+10))])
                count=0
            else:
                t=t+s[i]

        
        else:
            t=t+s[i]

    
    return(t)          
            
            
            



       