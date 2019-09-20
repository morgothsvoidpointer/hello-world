# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""



import tweepy
import bokeh
import datetime
import csv
import matplotlib
import math
#import pillow
import wordcloud
import networkx
import graphviz
import re
import urllib.request
import numpy as np
import pandas as pd
import json
import munch
import importlib  
GetOldTweets = importlib.import_module("GetOldTweets-python-master")



from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
import warnings
warnings.filterwarnings("ignore")

import os
import sys 


#internal imports
from twitter_orig_utils import *
from SocialistSunday import *
import patel1
import bokeh_utils

userhome = os.path.expanduser('~')
#python_dir=userhome+'/Documents/ThinkTank/library/python/python_other/word_match/'
python_dir=userhome+'/Documents/word_files_dir/'
save_dir=python_dir+'Output/'
if python_dir not in sys.path: sys.path.append(python_dir)


# Consumer keys and access tokens, used for OAuth
consumer_key = 'Xa8XbijTP7F3sg0QJ1QUoLq6f'
consumer_secret = 'cRBjxlQK3PO2cy4zFnfZGlLdtIYm1c9KMIe8IsZVaE0OqFIMsh'
access_token = '1092850952284131328-6prMHiiBPsQHU5In4xho9N1cQy9wpO'
access_token_secret = 'BOs3QPs7PnF8uRMgaexuv3BizPPkMeSdXq3YEqATcIsM9'



query='Epstein and Clinton'
read_from_file=0
max_tweets=1000

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
 
# Creation of the actual interface, using authentication
api = tweepy.API(auth,wait_on_rate_limit=True)

# Function to extract tweets 
def get_tweets_by_user(username,number_of_tweets=200): 
          

  
        # 200 tweets to be extracted 
        
        tweets = api.user_timeline(screen_name=username,tweet_mode="extended") 
  
        # Empty Array 
        tmp=[]  
  
        # create array of tweet information: username,  
        # tweet id, date/time, text 
        tweets_for_csv = [tweet.full_text for tweet in tweets] # CSV file created  
        for j in tweets_for_csv:
  
            # Appending tweets to the empty array tmp 
            tmp.append(j)  
  
        # Printing the tweets 
       # print(tmp)
        

        #saving
        with open(save_dir+"test.csv", mode='w') as log_file:
            log_writer = csv.writer(log_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            timest=datetime.datetime.now()
            log_writer.writerow(['log','extracted',timest])
            for j in tweets_for_csv:
                 log_writer.writerow([str(j).encode("utf-8")])

        return(tmp)    

#this function checks if info for a list of users has been retrieved already, and fills in the blanks by using the api
def user_group_info(author_list_tofind,author_list_found,user_info_found):
    present=[]
    send_list=[]
    for i in range(len(author_list_tofind)):
        if author_list_tofind[i] in author_list_found:
            present.append(1)
        elif author_list_tofind[i]=='nan':
            present.append(-1)
        else:
            present.append(0)
            send_list.append(author_list_tofind[i])
            
    send_list=list(set(send_list))
    
    #extract user info for a supplied user list 
    user_info=[]
    #split into batches of 100
    l=len(send_list)
    bounds_list=[]
    b=0
    while b+100<l:
       b=b+100
       bounds_list.append(b)
    bounds_list.append(l)
   
    
    for j in range(len(bounds_list)):
        if j==0:
            lwr=0
        else:
            lwr=bounds_list[j-1]
        upr=bounds_list[j]
        user_list_batch=send_list[lwr:upr]
        user_info.extend(get_usernames(user_list_batch)) #user_info is the batched user info import
    
    #merge with existent list
    

    
    author_info=[]
    for i in range(len(author_list_tofind)):
        if present[i]==0:
            for j in range(l):
                if (send_list[j]==author_list_tofind[i]):
                    break
            
            author_info.append(user_info[j])
        elif present[i]==1:
            for j in range(len(author_list_found)):
                if (author_list_found[j]==author_list_tofind[i]):
                    break
            author_info.append(user_info_found[j])
        elif present[i]==-1:
            author_info.append('nan')
    return([user_info,author_info])    
    
def query_tweets(save_file, query, lang="en", limit=max_tweets):
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
        
        
        
        
        
        searched_tweets = [status for status in tweepy.Cursor(api.search, q=query, tweet_mode='extended').items(max_tweets)]
              
        with open(save_file, mode='w') as log_file:
            log_writer = csv.writer(log_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            timest=datetime.datetime.now()
            log_writer.writerow(['log','extracted',timest])
            for j in searched_tweets:
                #print(str(j.full_text).encode('utf-8-sig'))
                log_writer.writerow([str(j.full_text).encode("utf-8-sig")])
        return searched_tweets
        
#word cloud
def word_cloud(status_list):

    texts=[]
    for i in range(len(status_list)):
        texts.append(str(status_list[i].full_text))
    stop_words = ["https", "co", "RT"] + list(STOPWORDS) 
    words=" ".join(texts)
    wordcloud_local = WordCloud(stopwords=stop_words, background_color="white",height=400,width=800,max_words=500).generate(words)
    plt.imshow(wordcloud_local, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    wordcloud_local.to_file(save_dir+"wc.png")

#extract links
def links_extract(status_list):
    links=[]
    sites=[]
    users=[]
    failed=[]
    for tweet in status_list:
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet.full_text)
        urls_actual = []
        sites_status=[]
        users_linked_status=[]
        urls_failed_status=[]
        for url in urls:
            try:
                res = urllib.request.urlopen(url)
                actual_url = res.geturl()
                #print actual_url
            except:
                print("url invalid "+url)
                urls_failed_status.append(url)                
            else:
                urls_actual.append(actual_url)
                slash_split=actual_url.split("/")
                site=slash_split[2]
                if site=="twitter.com":
                    user_linked=slash_split[3]
                    users_linked_status.append(user_linked)
                else:
                    sites_status.append(site)
                    #print(site)
        links.append(urls_actual)
        sites.append(sites_status)
        users.append(users_linked_status)
        failed.append(urls_failed_status)
    return [links,sites,users,failed]




#this function is just a small wrapper for the api method lookup_users
def get_usernames(ids):
    """ can only do lookup in steps of 100;
        so 'ids' should be a list of 100 ids
    """
    if len(ids)==0:
        print('empty object submitted to username fetcher')
        return 'nan'
    user_objs = api.lookup_users(screen_names=ids)
    return(user_objs)
    
def rt_author_extract(status_list):
    rt_author_record=[]
    for i in range(len(status_list)):
        rt_string="RT @"
        my_string=status_list[i].full_text
        if rt_string in my_string:
            T=my_string.split(rt_string)[1]
            U=T.split(':')[0]
            rt_author_record.append(U)
        else:
            rt_author_record.append("nan")
    
    return rt_author_record

def hash_extract(status_list):
    tag_list=[]
    for i in range(len(status_list)):
        tag_list_status=[]
        tweet=status_list[i].full_text
        cleaned = re.sub(r"[,.;@?!&$\n\r]+\ *", " ", tweet)
        cleaned_list=cleaned.split(" ")
        for j in range(len(cleaned_list)):
            if (cleaned_list[j].startswith('#')):
                tag_list_status.append(cleaned_list[j])
        tag_list.append(tag_list_status)
    return(tag_list)
    
#this function extracts the user info object from a tweet status object
def author_info_extract(status_list):
    user_info=[]
    author_record=[]
    for i in range(len(status_list)):
        author_record.append(0)
        user_info.append(0)
        if (type(status_list[i])==dict):
            author_record[i]=status_list[i]["user"]["screen_name"]
            user_info[i]=status_list[i]["user"]
        
        else:
            try:
                author_record[i]=status_list[i].user.screen_name
                user_info[i]=status_list[i].user
            except AttributeError:
                author_record[i]=status_list[i].author.screen_name
                user_info[i]=status_list[i].author        

    return [author_record,user_info]


#this function takes a list of objects and extracts the attribute specified by the string attr
def user_feature_extract(user_info_list,attr):
    out=[]
    if depth(user_info_list,exclude=(munch.Munch,str))==1:
        for i in range(len(user_info_list)):
            if (type(user_info_list[i])!=str):
                #print("i "+str(i))
                #print(user_info_list[i])
                out.append(getattr(user_info_list[i],attr))
            else:
                out.append(user_info_list[i])           
        return(out)
    elif depth(user_info_list,exclude=(munch.Munch,str))==2:
        for i in range(len(user_info_list)):
            out.append([])
            for j in range(len(user_info_list[i])):
                if (type(user_info_list[i][j])!=str):
                    out[i].append(getattr(user_info_list[i][j],attr))
                else:
                    out[i].append(user_info_list[i][j])
        return(out)
    else:
        print('list empty or of depth higher than 2')
        return(user_info_list)
        

#    G=node_attrs_add(author_full_info,G)

def node_attrs_add(user_list,G,attr_names=['created_at','followers_count','friends_count','favourites_count']):
    
    attributes_all={}
    for i in range(len(user_list)):
        for j in range(len(G.nodes)):
            if (list(G.nodes)[j]==user_list[i].screen_name):
                attributes={}
                for attr in attr_names:
                    attributes[attr]=getattr(user_list[i],attr)#for each node, we have an attribute dict
                break
        attributes_all[list(G.nodes)[j]]=attributes
    networkx.set_node_attributes(G,attributes_all)
    return(G)
    

#this function generates the RT graph from a list of 'retweet pairs'
def rt_net_generate(rt_list,na_replace="duplicate"):
    if na_replace=="duplicate":
        for i in rt_list:
            if i[0]=="nan":
                i[0]=i[1]
            if i[1]=="nan":
                i[1]=i[0]     
    edge_list=[(rt_list[i][0],rt_list[i][1]) for i in range(len(rt_list))]
    #print(edge_list)
    G = networkx.Graph()
    attr_values=iter(range(len(edge_list)))
    for edge in edge_list:
        #print(edge)
        G.add_edges_from([edge],label=attr_values.__next__())
    
    #print(G.edges)
    
    return G

#this function generates and also plots the RT graph
def rt_net_plot(rt_list,node_colours=0,na_replace="duplicate"):
    G=rt_net_generate(rt_list,na_replace="duplicate")
   
    if node_colours:
        with open(F_NAME_AFFILIATIONS,'r') as f_in:
            reader    = csv.reader(f_in, delimiter=',', quotechar='"')
            headers    = next(reader);
            mp_mep_affiliation = {row[2]:row[5] for row in reader}
        
        color_map = {
            'Conservative':'#00539F',
            'Labour':'#E4003B',
            'Scottish National Party':'#FFF685',
            'United Kingdom Independence Party':'#8C4E9A',
            'Democratic Unionist Party':'#19283E',
            'Liberal Democrat':'#FECB0E',
            'Green Party':'#78B82A',
            'Social Democratic and Labour Party':'#F89828',
            'Plaid Cymru':'#3F8429',
            'Sinn Fein':'#F99D1D',
            'Ulster Unionist Party':'#213362',
            'Independent':'#D3D3D3'}

        for node in G.nodes():
            G.node[node]['party'] = mp_mep_affiliation[node]

        
    pos = networkx.spring_layout(G, k = 1, iterations = 200)
    #pos2 = graphviz_layout(G)
    
    cut = 0.02
    xmin, xmax = min(xx for xx,yy in pos.values()), max(xx for xx,yy in pos.values())
    ymin, ymax = min(yy for xx,yy in pos.values()), max(yy for xx,yy in pos.values())
    fig = matplotlib.pyplot.figure(1, figsize=(10,10))
    if node_colours:
        networkx.draw(G, pos, node_size = 20, node_color = [color_map[G.node[node]['party']] for node in G])
        #networkx.draw(G, pos2, node_size = 20, node_color = [color_map[G.node[node]['party']] for node in G])
    else:
        Colors=range(len(G))
        
        networkx.draw(G, pos, node_size = 20, node_color = Colors,with_labels=True)
        #networkx.draw(G, pos2, node_size = 20, node_color = Colors,with_labels=True)
      #  networkx.draw_network_labels(G)
    
    matplotlib.pyplot.xlim(xmin - cut * (xmax - xmin), xmax + cut * (xmax - xmin))
    matplotlib.pyplot.ylim(ymin - cut * (ymax - ymin), ymax + cut * (ymax - ymin))
    #matplotlib.pyplot.title('MP/MEP retweet network %s to %s' % (start_date.isoformat(), end_date.isoformat()))
    matplotlib.pyplot.show()
    

    
    return G

def components_asgraphs(G):
    return((G.subgraph(c) for c in networkx.connected_components(G)))
    
def components_plot(G):
    comp_list=list(components_asgraphs(G))
    c_size_1=[]
    c_size_2=[]
    for subgraph in comp_list:
        sz=subgraph.number_of_nodes()
        if sz==1:
            c_size_1.append(subgraph.nodes())
        elif sz==2:
            c_size_2.append(subgraph.nodes())
        else:
            node_highest=keywithmaxval(dict(networkx.degree(subgraph)))
            
            file_string=save_dir+"q="+query+"_h="+node_highest+"_d="+str(sz)+".gexf"
            graph_to_gephi(subgraph,filename=file_string)
    return([c_size_1,c_size_2])
    
#this function takes in a status list and a component subdivision and returns the indices for each component. 
def list_components_split(rt_list):    
    indices=[]
    G=rt_net_generate(rt_list,na_replace="duplicate")
    Comps=networkx.connected_components(G)#returns an iterator
    Indlist=[]
    Complist={}
    Edgelist={}
    Edgeind={}
    attrs_dict=networkx.get_edge_attributes(G,"label")
    j=-1
    for i in range(len(G)):#dummy index - in reality the number of components will be smaller than the size of G
        j=j+1
        try:
            Ind_comp=next(Comps)#gives a set of nodes in the component
        except StopIteration:
            break
        #print(Ind_comp)
        Indlist.extend(Ind_comp)
        for vx in Ind_comp:
            Complist[vx]=j#label each vertex by the component
            ed=list(G.edges(vx))
            for edge in ed:
                #print(edge)
                #print(attrs_dict)
                try:
                    l=attrs_dict[edge]
                except KeyError:
                    edge=edge[::-1]
                    l=attrs_dict[edge]
                #print("edge attributes")

                #print(l)
                Edgelist[edge]=j#label each edge by the component
                Edgeind[l]=j
    return [G,Complist,Edgelist,Edgeind]   
    
    #G is the graph, Indlist is the list of indices, Complist is the (vx label to component number) dict
    #Edgelist is the (edge index to component number dict). Edge index should be the same as the index of the corresponding tweet.
    
def status_list_split(status_list,rt_list):
    [G,Complist,Edgelist,Edgeind]=list_components_split(rt_list)
    user_groups=[]
    rt_groups=[]
    for i in np.unique(list(Complist.values())):
        user_groups.append([k for k,v in Complist.items() if v == i])
    for i in np.unique(list(Edgeind.values())):
        rt_groups.append(0)
        print(Edgeind.items())
        print(i)
        rt_groups[i]=[status_list[k] for k,v in Edgeind.items() if v == i] 

    return [user_groups,rt_groups]




def graph_to_gephi(G,filename="test.gexf"):
    networkx.write_gexf(G,filename)
    print("duh")
    
# Driver code 
if __name__ == '__main__': 
  
    # Here goes the twitter handle for the user 
    # whose tweets are to be extracted. 
    #get_tweets_by_user("AbiWilks")
    #or by query
    

    if not read_from_file: 
        #check directory to save to exists first
        save_file=save_dir+"fresh_dump_q="+query+".txt"
        
        if not os.path.isdir(save_dir):
            print("warning: create the directory")
        
        searched_tweets=query_tweets(save_file=save_file, query=query, lang="en", limit=max_tweets)#search twitter according to query

        [author_list,author_full_info]=author_info_extract(status_list=searched_tweets)#extract the tweet author name and object
        
        retweet_author_list=rt_author_extract(status_list=searched_tweets)#extract the original author of any RT's
        
        author_list_found=author_list
        author_list_tofind=retweet_author_list
        user_info_found=author_full_info
        
        [_,author_full_info_rt]=user_group_info(author_list_tofind,author_list_found,user_info_found)#extract the author info from retweet original authors
        
        
        
        L=lists_combine_col(retweet_author_list,author_list)#combine the name lists
        L2=lists_combine_col(author_full_info_rt,author_full_info)#combine the extra info
        
        L3=list_prune(L2)#remove repeats
        file_string=save_dir+"q="+query+"_rt_graph.txt"
        list_write(filepath=file_string,the_list=L)#write the name lists
        M=L
        
        #save the full tweets
        file_string_json=save_dir+"q="+query+"_rt_graph.json"
        with open(file_string_json, 'w') as out:
            out.write(json.dumps([status._json for status in searched_tweets]))

        #print(tag_list)
        
    if read_from_file:

        file_string_json=save_dir+"q="+query+"_rt_graph.json"
        with open(file_string_json) as json_file:
            searched_tweets = munch.munchify(json.load(json_file))
        
        
        
        [author_list,author_full_info]=author_info_extract(status_list=searched_tweets)#extract the tweet author name and object
        
        retweet_author_list=rt_author_extract(status_list=searched_tweets)#extract the original author of any RT's
        
        author_list_found=author_list
        author_list_tofind=retweet_author_list
        user_info_found=author_full_info
        
        [_,author_full_info_rt]=user_group_info(author_list_tofind,author_list_found,user_info_found)#extract the author info from retweet original authors
        
        
        
        L=lists_combine_col(retweet_author_list,author_list)#combine the name lists
        
        L2=lists_combine_col(author_full_info_rt,author_full_info)#combine the extra info
        
        L3=list_prune(L2)
#        
#        for i in range(len(L3)):
#            print(isinstance(L3[i],dict))
#            
#        for i in range(len(L2)):
#            print(0)
#            print(isinstance(L2[i][0],dict))      
#            print(1)
#            print(isinstance(L2[i][1],dict))  
        
        
        M=array_load(filepath=save_dir+"q="+query+"_rt_graph.txt")
        
    #graph build
    G=rt_net_plot(M)
    [G,Vx,Ed,Edi]=list_components_split(M)
    
    [user_groups,rt_groups]=status_list_split(searched_tweets,M)
    
    #add attrs to G
    G=node_attrs_add(author_full_info,G)
    
    #save to gephi format
    filename=save_dir+query+"_rt_graph"+".gexf"
    graph_to_gephi(G,filename)
    G_Components=list(components_asgraphs(G))
    [singletons,doubletons]=components_plot(G)
    
    #vx info
    print(user_groups)
    
    name_labels=user_feature_extract(L3,'screen_name')
    
    user_info_by_component=[]
    
    #rearrange the user info according to the component list
    for i in range(len(user_groups)):
        user_info_by_component.append([])
        for j in range(len(user_groups[i])):
            u=user_groups[i][j]
            for k in range(len(name_labels)):
                if name_labels[k]==u:
                    
                    user_info_by_component[i].append(L3[k])
                    break
                    
    #now extract
    name_labels_check=user_feature_extract(user_info_by_component,'screen_name')
    
    
    #created_at
    created=user_feature_extract(user_info_by_component,'created_at')
    #followers_count
    followers=user_feature_extract(user_info_by_component,'followers_count')
    #friends_count
    followed=user_feature_extract(user_info_by_component,'friends_count')
    #favourites_count           
    liked=user_feature_extract(user_info_by_component,'favourites_count')
    
    print(created)
    print(followers)
    print(followed)
    print(liked)
    
    #edge info
    tag_list=hash_extract(status_list=searched_tweets)#extract tags for each tweet
    #break into components
    #print(user_groups)
    tag_component_list=[]
    for i in range(len(rt_groups)):
        tag_component_list.append(hash_extract(status_list=rt_groups[i]))
        
    print(tag_component_list)   
        
        
    #links
    [links,sites,users,failed]=links_extract(searched_tweets)#extract links for each tweet
    #break into components
    
    sites_component=[]
    for i in range(len(rt_groups)):
        sites_component.append(0)
        [_,sites_component[i],_,_]=links_extract(rt_groups[i])
    print(sites_component)
    
    #word clouds
    word_cloud(status_list=searched_tweets)
    for i in range(len(rt_groups)):
        word_cloud(status_list=rt_groups[i])
    
    filename=save_dir+"temp.json"
    patel1.save_json(L3,filename)
    L4=patel1.load_json(filename)
    #histograms
    filename="test.json"
    user_objects=L4
    
    
        
    h_set,f_set=bokeh_utils.creation_histogram(user_objects,filename)
    from bokeh.plotting import figure
    from bokeh.io import show, output_notebook
    arr_hist, edges = np.histogram(vec_freq_convert(h_set), 
                               bins = int(2000/10), 
                               range = [0, 700])
    
    delays = pd.DataFrame({'arr_delay': arr_hist, 
                       'left': edges[:-1], 
                       'right': edges[1:]})
    
    p = figure(plot_height = 600, plot_width = 600, 
           title = 'Weeks since account creation',
           x_axis_label = 'no. weeks', 
           y_axis_label = 'Frequency')

    # Add a quad glyph
    p.quad(bottom=0, top=delays['arr_delay'], 
       left=delays['left'], right=delays['right'], 
       fill_color='red', line_color='black')
    
    
    show(p)
    #results and component-based results
    def Sorting(lst): 
        lst.sort(key=len) 
        return lst 

    
    Cli=networkx.enumerate_all_cliques(G)

    Cli_list=list(Cli)
    
    S=Sorting(Cli_list)
    
    L=[len(s) for s in S]
    M=[len(G_comp) for G_comp in G_Components]
    
    sys.stdout.flush()

    

    #graph analysis
    
    
    #cliques
    

    
    
    
    
    
    
    
