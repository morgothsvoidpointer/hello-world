# -*- coding: utf-8 -*-
from tensorflow.contrib.tensorboard.plugins import projector
from sklearn.manifold import TSNE
from collections import Counter
from six.moves import cPickle
import gensim.models.word2vec as w2v
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import multiprocessing
import os
import sys
import io
import re
import json
import nltk
from nltk.corpus import wordnet
from collections import Iterable
import copy

from index_functions import *
from index_functions import query_locate,text_scan,bigrams_find,flatten,list_to_string,sublist_consec,sentence_quick_clean, stop_search
from nltk_functions import bigrams_adj_clean,part_add


wvfile="word_vectors.w2v"
vocab_vectors="vocab_vectors.npy"
labelsfile="labels.json"
xcorfile="x_coords.npy"
ycorfile="y_coords.npy"
plotdir="plots"
assoc="associations.csv"
caps_only=False
quotes_extract=True

brackets_remove=1 #remove brackets from tokenised text
quotes_remove=0 #remove quotes from tokenised text
group_on=1

text_stop="234917394273948273940878970"#string at which to stop processing the text

def try_load_or_process(filename, processor_fn, function_arg1, function_arg2, must_process=0):
  load_fn = None
  save_fn = None
  if filename.endswith("json"):
    load_fn = load_json
    save_fn = save_json
  else:
    load_fn = load_bin
    save_fn = save_bin
  if os.path.exists(filename) and not must_process:
    return load_fn(filename)
  else:
    ret = processor_fn(function_arg1, function_arg2)
    save_fn(ret, filename)
    return ret
 
def print_progress(current, maximum):
  sys.stdout.write("\r")
  sys.stdout.flush()
  sys.stdout.write(str(current) + "/" + str(maximum))
  sys.stdout.flush()
 
def save_bin(item, filename):
  with open(filename, "wb") as f:
    cPickle.dump(item, f)
 
def load_bin(filename):
  if os.path.exists(filename):
    with open(filename, "rb") as f:
      return cPickle.load(f)
 
def save_json(variable, filename):
  with io.open(filename, "w", encoding="utf-8") as f:
    f.write(str(json.dumps(variable, indent=4, ensure_ascii=False)))

def load_json(filename):
  ret = None
  if os.path.exists(filename):
    try:
      with io.open(filename, "r", encoding="utf-8") as f:
        ret = json.load(f)
    except:
      pass
  return ret

def process_raw_data(input_file,extra_stopwords):
  valid = u"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ#@.,:/ -'‘’āäöåÄÖÅÆæǢǣǼáǽæ̀úóëêðñûîí()"
  url_match = "(https?:\/\/[0-9a-zA-Z\-\_]+\.[\-\_0-9a-zA-Z]+\.?[0-9a-zA-Z\-\_]*\/?.*)"
  name_match = "\@[\_0-9a-zA-Z]+\:?"
  lines = []
  print("Loading raw data from: " + input_file)
  if os.path.exists(input_file):
    with io.open(input_file, 'r', encoding="utf-8") as f:
      lines = f.readlines()
  num_lines = len(lines)
  ret = []
  for count, text in enumerate(lines):

    if count % 50 == 0:
      print_progress(count, num_lines)
    text = re.sub(url_match, u"", text)
    text = re.sub(name_match, u"", text)
    text = re.sub("\&amp\;?", u"", text)
    text = re.sub("[\:\.]{1,}$", u"", text)
    text = re.sub("^RT\:?", u"", text)

    text = re.sub("\’s ","@ ",text)
    text = re.sub("\'s ","@ ",text)
    #print(text)
    text = re.sub("\s+\.","\.",text)
    
    text = re.sub("’d","d",text)
    text = re.sub("’st","st",text)
    
    #print(text)
    if ("extempore" in text):
        print(text)
    #text=re.sub("[\[]].*?[\]", "", x) #to remove text in sq brackets
    text = u''.join(x for x in text if x in valid)
    if ("extempore" in text):
        print(text)
    text = text.strip()
    if len(text.split()) > 5:
      if text not in ret:
        ret.append(text)
    if (text_stop in text):
        break
  return ret

def process_raw_string(input_strings,extra_stopwords):
  valid = u"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ#@.,:/ -'āäöåÄÖÅÆæǢǣǼǽæ̀úóëéûüíÓ()"
  url_match = "(https?:\/\/[0-9a-zA-Z\-\_]+\.[\-\_0-9a-zA-Z]+\.?[0-9a-zA-Z\-\_]*\/?.*)"
  name_match = "\@[\_0-9a-zA-Z]+\:?"

  num_lines = len(input_strings)
  ret = []
  for count, text in enumerate(input_strings):
    if count % 50 == 0:
      print_progress(count, num_lines)
    text = re.sub(url_match, u"", text)
    text = re.sub(name_match, u"", text)
    text = re.sub("\&amp\;?", u"", text)
    text = re.sub("[\:\.]{1,}$", u"", text)
    text = re.sub("^RT\:?", u"", text)
    text = re.sub("[\(].*?[\)]", "", text) #to remove text in round brackets
    #text=re.sub("[\[]].*?[\]", "", x) #to remove text in sq brackets
    text = u''.join(x for x in text if x in valid)
    text = text.strip()
    ret.append(text)
  return ret

def quotes_extract(text):
    l = re.split("[‘’]+",text)[1::2]
    return(l)

def quotes_extract2(text,start,end):
    l1=text.split(start)
    if len(l1)==0:
        return(text)
    else:
        l2=[]
        for i in range(len(l1)):
            if i==0:
                continue
            q=l1[i].split(end)
            if len(q)>1:
                l2.append(q[0])
    return(l2)



def quotes_extract3(text,start,end):
    l1=text.split(start)
    if len(l1)==0:
        return(text)
    else:
        l2=[]
        for i in range(len(l1)):
            if i==0:
                continue
            q=l1[i].split(end)
            if len(q)>1:
                l2.append(q[0])
    return(l2)
                
def cap_or_bust(word):
    if caps_only:
        return None
    else:
        return word.lower()

def caps_remove(word_prev,word):
    if len(word)==0:
        return word
    
    #detect if word capitalised
    if not word[0].isupper():
        return cap_or_bust(word)#we de-capitalise the first word in the sentence
    else:
        lastc=word_prev[-1]
        if lastc=='!' or lastc=='?':
            return cap_or_bust(word)
        elif lastc=='.':
            if len(word_prev)<3:
                return word
            else:
                return cap_or_bust(word)
        else:
            return word
        
def tokenize_sentences(sentences,  extra_stopwords):
    
    
    
  ret = []
  max_s = len(sentences)
  print("Got " + str(max_s) + " sentences.")
  for count, s in enumerate(sentences):
    if brackets_remove:
        s = re.sub("[\(].*?[\)]", "", s) #to remove text in round brackets  
    if quotes_remove:
        s = re.sub(" [‘].*?[’]", "", s)
        s = re.sub("[‘].*?[’]", "", s)
        s = re.sub("s’","s@",s)
    else:
        s=quote_det(s)
        s = re.sub("s’","s@",s)
        s = re.sub("’","",s)        
    
    tokens = []
    words = re.split(r'(\s+)', s)
    if len(words) > 0:
      wlast=None
      for w in words:
        if w is not None:
          if wlast is None:
              w_out = cap_or_bust(w)
          else:
              #print(w)
              w_out = caps_remove(wlast,w)
              #print(w)
          if w.isspace() or w == "\n" or w == "\r":
            w_out = None
            w = None
          elif len(w) < 1:
            w_out = None
            w = None
          if w_out is not None:
            tokens.append(w_out)
            wlast=w
          elif caps_only and w is not None:
            wlast=w
    if len(tokens) > 0:
      ret.append(tokens)
    if count % 50 == 0:
      print_progress(count, max_s)
  return ret

def clean_sentences(tokens,extra_stopwords,remove_possessive=True):
  all_stopwords = load_json("stopwords-iso.json")
  #print(all_stopwords)
  #extra_stopwords = ["ssä", "lle", "h.", "oo", "on", "muk", "kov", "km", "ia", "täm", "sy", "but", ":sta", "hi", "py", "xd", "rr", "x:", "smg", "kum", "uut", "kho", "k", "04n", "vtt", "htt", "väy", "kin", "#8", "van", "tii", "lt3", "g", "ko", "ett", "mys", "tnn", "hyv", "tm", "mit", "tss", "siit", "pit", "viel", "sit", "n", "saa", "tll", "eik", "nin", "nii", "t", "tmn", "lsn", "j", "miss", "pivn", "yhn", "mik", "tn", "tt", "sek", "lis", "mist", "tehd", "sai", "l", "thn", "mm", "k", "ku", "s", "hn", "nit", "s", "no", "m", "ky", "tst", "mut", "nm", "y", "lpi", "siin", "a", "in", "ehk", "h", "e", "piv", "oy", "p", "yh", "sill", "min", "o", "va", "el", "tyn", "na", "the", "tit", "to", "iti", "tehdn", "tlt", "ois", ":", "v", "?", "!", "&"]
  #extra_extra_stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
  
  stopwords = None
  if all_stopwords is not None:
    stopwords = all_stopwords
    stopwords += extra_stopwords
    #stopwords += extra_extra_stopwords
  ret = []
  max_s = len(tokens)
  for count, sentence in enumerate(tokens):
    if count % 50 == 0:
      print_progress(count, max_s)
    cleaned = []
    for token in sentence:
      if len(token) > 0:
        
        #print(token)
        if re.search("^[0-9\.\-\s\/]+$", token):
          token = None
        elif re.search("([0-9])",token):
          token = None
        elif re.search("^[a-z]{1}\\.",token):
          #print(token)
          token = None
        elif re.search("^[A-Z]{1}\\.",token):
          #print(token)
          token = None       
        elif re.search("^[i]\\.",token):
          #print(token)
          token = None
        elif re.search("^[0-9]{4}\:",token):
          token = None
        elif re.search("^[0-9]{3}",token):
          token = None
        elif token=="-":
          token = None
        else:
          token=token.replace(".","")

          token=token.replace(":","")
          
          token=token.replace(",","")
          
          if remove_possessive:
              token=token.replace("@","")
          
          #token=token.replace("s'","")
        if token=="":
            token=None
        if token is not None:
            t1=token
            t2=token.lower()
            if stopwords is not None:
              for s in stopwords:
                if t1==s or t2==s:
                  token = None
        if token is not None:
            cleaned.append(token)
    if len(cleaned) > 0:
      ret.append(cleaned)
  return ret

def get_word_frequencies(corpus,  extra_stopwords):
  frequencies = Counter()
  for sentence in corpus:
    for word in sentence:
      frequencies[word] += 1
  freq = frequencies.most_common()
  return freq

# The following function accepts the tokenized and cleaned data generated from the steps above, and uses it to train a word2vec model. The num_features parameter sets the number of features each word is assigned (and hence the dimensionality of the resulting tensor.) It is recommended to set it between 100 and 1000. Naturally, larger values take more processing power and memory/disk space to handle. I found 200 to be enough, but I normally start with a value of 300 when looking at new datasets. The min_count variable passed to word2vec designates how to trim the vocabulary. For example, if min_count is set to 3, all words that appear in the data set less than 3 times will be discarded from the vocabulary used when training the word2vec model. In the dimensionality reduction step we perform later, large vocabulary sizes cause T-SNE iterations to take a long time. Hence, I tuned min_count to generate a vocabulary of around 10,000 words. Increasing the value of sample, will cause word2vec to randomly omit words with high frequency counts. I decided that I wanted to keep all of those words in my analysis, so it’s set to zero. Increasing epoch_count will cause word2vec to train for more iterations, which will, naturally take longer. Increase this if you have a fast machine or plenty of time on your hands




def get_word2vec(sentences):
  num_workers = multiprocessing.cpu_count()
  num_features = 1000
  epoch_count = 10
  sentence_count = len(sentences)
  w2v_file = os.path.join(save_dir, wvfile)
  word2vec = None
  if os.path.exists(w2v_file):
    print("w2v model loaded from " + w2v_file)
    word2vec = w2v.Word2Vec.load(w2v_file)
  else:
    word2vec = w2v.Word2Vec(sg=1,
                            seed=1,
                            workers=num_workers,
                            size=num_features,
                            min_count=min_frequency_val,
                            window=2,
                            sample=0)
 
    print("Building vocab...")
    word2vec.build_vocab(sentences)
    print("Word2Vec vocabulary length:", len(word2vec.wv.vocab))
    print("Training...")
    word2vec.train(sentences, total_examples=sentence_count, epochs=epoch_count)
    print("Saving model...")
    word2vec.save(w2v_file)
  return word2vec

#Tensorboard has some good tools to visualize word embeddings in the word2vec model we just created. These visualizations can be accessed using the “projector” tab in the interface. Here’s code to create tensorboard embeddings:

def create_embeddings(word2vec):
  all_word_vectors_matrix = word2vec.wv.syn0
  num_words = len(all_word_vectors_matrix)
  vocab = word2vec.wv.vocab.keys()
  vocab_len = len(vocab)
  print("creating embeddings, vocab length "+str(vocab_len))
  dim = word2vec.wv[list(vocab)[0]].shape[0]
  embedding = np.empty((num_words, dim), dtype=np.float32)
  metadata = ""
  for i, word in enumerate(vocab):
    embedding[i] = word2vec.wv[word]
    metadata += word + "\n"
  metadata_file = os.path.join(save_dir, "metadata.tsv")
  with io.open(metadata_file, "w", encoding="utf-8") as f:
    f.write(metadata)
 
  tf.reset_default_graph()
  sess = tf.InteractiveSession()
  X = tf.Variable([0.0], name='embedding')
  place = tf.placeholder(tf.float32, shape=embedding.shape)
  set_x = tf.assign(X, place, validate_shape=False)
  sess.run(tf.global_variables_initializer())
  sess.run(set_x, feed_dict={place: embedding})
 
  summary_writer = tf.summary.FileWriter(save_dir, sess.graph)
  config = projector.ProjectorConfig()
  embedding_conf = config.embeddings.add()
  embedding_conf.tensor_name = 'embedding:0'
  embedding_conf.metadata_path = 'metadata.tsv'
  projector.visualize_embeddings(summary_writer, config)
 
  save_file = os.path.join(save_dir, "model.ckpt")
  print("Saving session...")
  saver = tf.train.Saver()
  saver.save(sess, save_file)
  
def most_similar(input_word, num_similar):
  sim = word2vec.wv.most_similar(input_word, topn=num_similar)
  output = []
  found = []
  for item in sim:
    w, n = item
    found.append(w)
  output = [input_word, found]
  return output

#The following function takes a list of words to be queried, passes them to the above function, saves the output, and also passes the queried words to t_sne_scatterplot(), which we’ll show later. It also writes a csv file – associations.csv – which can be imported into Gephi to generate graphing visualizations. 

def test_word2vec(test_words):
  vocab = word2vec.wv.vocab.keys()
  vocab_len = len(vocab)
  print("testing, vocab length is ",str(vocab_len))
  output = []
  associations = {}
  test_items = test_words
  for count, word in enumerate(test_items):
    if word in vocab:
      print("[" + str(count+1) + "] Testing: " + word)
      if word not in associations:
        associations[word] = []
      similar = most_similar(word, num_similar)
      t_sne_scatterplot(word)
      output.append(similar)
      for s in similar[1]:
        if s not in associations[word]:
          associations[word].append(s)
    else:
      print("Word " + word + " not in vocab")
  filename = os.path.join(save_dir, "word2vec_test.json")
  save_json(output, filename)
  filename = os.path.join(save_dir, "associations.json")
  save_json(associations, filename)
  filename = os.path.join(save_dir, assoc)
  handle = io.open(filename, "w", encoding="utf-8")
  handle.write(u"Source,Target\n")
  for w, sim in associations.items():
    for s in sim:
      handle.write(w + u"," + s + u"\n")
  return output

#The next function implements standalone code for creating a scatterplot from the output of T-SNE on a set of data points obtained from a word2vec.wv.most_similar() query. The scatterplot is visualized with matplotlib.

def t_sne_scatterplot(word):
  vocab = word2vec.wv.vocab.keys()
  vocab_len = len(vocab)
  print("creating scatter plot, vocab length is "+str(vocab_len))
  dim0 = word2vec.wv[list(vocab)[0]].shape[0]
  arr = np.empty((0, dim0), dtype='f')
  w_labels = [word]
  nearby = word2vec.wv.similar_by_word(word, topn=num_similar)
  arr = np.append(arr, np.array([word2vec[word]]), axis=0)
  for n in nearby:
    w_vec = word2vec[n[0]]
    w_labels.append(n[0])
    arr = np.append(arr, np.array([w_vec]), axis=0)
 
  tsne = TSNE(n_components=2, random_state=1)
  np.set_printoptions(suppress=True)
  Y = tsne.fit_transform(arr)
  x_coords = Y[:, 0]
  y_coords = Y[:, 1]
 
  plt.rc("font", size=16)
  plt.figure(figsize=(16, 12), dpi=80)
  plt.scatter(x_coords[0], y_coords[0], s=800, marker="o", color="blue")
  plt.scatter(x_coords[1:], y_coords[1:], s=200, marker="o", color="red")
 
  for label, x, y in zip(w_labels, x_coords, y_coords):
    plt.annotate(label.upper(), xy=(x, y), xytext=(0, 0), textcoords='offset points')
  plt.xlim(x_coords.min()-50, x_coords.max()+50)
  plt.ylim(y_coords.min()-50, y_coords.max()+50)
  filename = os.path.join(plot_dir, word + "_tsne.png")
  plt.savefig(filename)
  plt.close()


#In order to create a scatterplot of the entire vocabulary, we need to perform T-SNE over that whole dataset. This can be a rather time-consuming operation. The next function performs that operation, attempting to save and re-load intermediate steps (since some of them can take over 30 minutes to complete).
def calculate_t_sne():
  vocab = word2vec.wv.vocab.keys()
  vocab_len = len(vocab)
  arr = np.empty((0, dim0), dtype='f')
  labels = []
  vectors_file = os.path.join(save_dir, vocab_vectors)
  labels_file = os.path.join(save_dir, labelsfile)
  if os.path.exists(vectors_file) and os.path.exists(labels_file):
    print("Loading pre-saved vectors from disk")
    arr = load_bin(vectors_file)
    labels = load_json(labels_file)
  else:
    print("Creating an array of vectors for each word in the vocab")
    for count, word in enumerate(vocab):
      if count % 50 == 0:
        print_progress(count, vocab_len)
      w_vec = word2vec[word]
      labels.append(word)
      arr = np.append(arr, np.array([w_vec]), axis=0)
    save_bin(arr, vectors_file)
    save_json(labels, labels_file)
 
  x_coords = None
  y_coords = None
  x_c_filename = os.path.join(save_dir, xcorfile)
  y_c_filename = os.path.join(save_dir, ycorfile)
  if os.path.exists(x_c_filename) and os.path.exists(y_c_filename):
    print("Reading pre-calculated coords from disk")
    x_coords = load_bin(x_c_filename)
    y_coords = load_bin(y_c_filename)
  else:
    print("Computing T-SNE for array of length: " + str(len(arr)))
    tsne = TSNE(n_components=2, random_state=1, verbose=1)
    np.set_printoptions(suppress=True)
    Y = tsne.fit_transform(arr)
    x_coords = Y[:, 0]
    y_coords = Y[:, 1]
    print("Saving coords.")
    save_bin(x_coords, x_c_filename)
    save_bin(y_coords, y_c_filename)
  return x_coords, y_coords, labels, arr

#The next function takes the data calculated in the above step, and data obtained from test_word2vec(), and plots the results from each word queried on the scatterplot of the entire vocabulary. 

def show_cluster_locations(results, labels, x_coords, y_coords):
  for item in results:
    name = item[0]
    print("Plotting graph for " + name)
    similar = item[1]
    in_set_x = []
    in_set_y = []
    out_set_x = []
    out_set_y = []
    name_x = 0
    name_y = 0
    for count, word in enumerate(labels):
      xc = x_coords[count]
      yc = y_coords[count]
      if word == name:
        name_x = xc
        name_y = yc
      elif word in similar:
        in_set_x.append(xc)
        in_set_y.append(yc)
      else:
        out_set_x.append(xc)
        out_set_y.append(yc)
    plt.figure(figsize=(16, 12), dpi=80)
    plt.scatter(name_x, name_y, s=400, marker="o", c="blue")
    plt.scatter(in_set_x, in_set_y, s=80, marker="o", c="red")
    plt.scatter(out_set_x, out_set_y, s=8, marker=".", c="black")
    filename = os.path.join(big_plot_dir, name + "_tsne.png")
    plt.savefig(filename)
    plt.close()

def nounlist_construct(frequencies,tokens,stopwords):
  
  tokens_extended=copy.deepcopy(tokens)
  frequencies_single=copy.deepcopy(frequencies)
  
  min_occur=0
  


  for n_iter in range(4):
      
      frequencies_single=[list(elem) for elem in frequencies_single]
      
      parts_list=part_add(frequencies_single)
        
      #extract nouns
      nouns_list=[]
      for entry in parts_list:
          if entry[2]=='NNS':
              nouns_list.append([entry[0][:-1],entry[1],entry[2]])
          elif entry[2]=='NN' or entry[2]=='NNP':
              nouns_list.append(entry)
      
      for i in range(len(nouns_list)-1):
          for j in range(i+1,len(nouns_list)):
              if nouns_list[i][0]==nouns_list[j][0]:
                  nouns_list[i][1]=nouns_list[i][1]+nouns_list[j][1]
                  nouns_list[j][1]=0
      
      nouns_list_main=[]
      pronouns_list_main=[]
      thr=0
      for i in range(len(nouns_list)):
          if nouns_list[i][1]>thr:
              if not nouns_list[i][0][0].isupper():
                  nouns_list_main.append(nouns_list[i])
               
              
              else:
                  pronouns_list_main.append(nouns_list[i])
      
        
      #write to file
      
      noun_file="nouns.csv"
      noun_path=os.path.join(save_dir, noun_file)
      pronoun_file="pronouns.csv"
      pronoun_path=os.path.join(save_dir, pronoun_file)
      pronoun_file_plus="pronouns_plus%s.csv" % n_iter
      pronoun_path_plus=os.path.join(save_dir, pronoun_file_plus)    
      
      with open(noun_path, "w") as f:
        for s in nouns_list_main:
            f.write(str(s) +"\n")
      
      with open(pronoun_path, "w") as f:
        for s in pronouns_list_main:
            f.write(str(s) +"\n")
        all_stopwords = load_json("stopwords-iso.json")
     
      stopwords = None
      if all_stopwords is not None:
        stopwords = all_stopwords
        stopwords += extra_stopwords
              
            
      
      pronouns=pronouns_list_main
      with open(pronoun_path_plus, "w") as f:
        for s in pronouns:
           f.write(str(s) +"\n")       
      if 1:

        parts_list=nltk_functions.part_add(frequencies_single)
            

            
        #extract nouns
        nouns_list=[]
        for entry in parts_list:
            if entry[2]=='NNS':
                nouns_list.append([entry[0][:-1],entry[1],entry[2]])
            elif entry[2]=='NN' or entry[2]=="PST":
                nouns_list.append(entry)
          
        for i in range(len(nouns_list)-1):
            for j in range(i+1,len(nouns_list)):
                if nouns_list[i][0]==nouns_list[j][0]:
                    nouns_list[i][1]=nouns_list[i][1]+nouns_list[j][1]
                    nouns_list[j][1]=0
          
        nouns_list_main=[]
        pronouns_list_main=[]
        thr=0
        for i in range(len(nouns_list)):
            if nouns_list[i][1]>thr:
                if not nouns_list[i][0][0].isupper():
                    nouns_list_main.append(nouns_list[i])
                   
                  
                else:
                    pronouns_list_main.append(nouns_list[i])
            
        
        
        
        n_left=[]
        n_right=[]
        for word1 in pronouns:
            print(word1)
            n_left.append([])
            n_right.append([])
            for sentence in tokens_extended:
                #print(sentence)
                if word1[0] in sentence:
                    for count,word in enumerate(sentence):
                        #print(word)
                        #print(word1)
                        if word==word1[0]:
                            sleft=stop_search(sentence,stopwords,count,-1,1)
                            if not len(sleft)==0:
                                sl=sleft[0][0].isupper()
                                if sl:
                                    n_left[len(n_left)-1].append(sleft)
                            sright=stop_search(sentence,stopwords,count,1,1)
                            if not len(sright)==0:
                                sr=sright[-1][0].isupper()
                                if sr:
                                    n_right[len(n_right)-1].append(sright)
                if word1[0]+"s" in sentence:
                     for count,word in enumerate(sentence):
                        #print(word)
                        #print(word1)
                        if word==word1[0] or word==(word1[0]+"s"):
                            sleft=stop_search(sentence,stopwords,count,-1,1)
                            if not len(sleft)==0:
                                sl=sleft[0][0].isupper()
                                if sl:
                                    n_left[len(n_left)-1].append(sleft)
                            sright=stop_search(sentence,stopwords,count,1,1)
                            if not len(sright)==0:
                                sr=sright[-1][0].isupper()
                                if sr:
                                    n_right[len(n_right)-1].append(sright)               
                    
                    
                            
        for i in range(len(n_right)):
            for j in range(len(n_right[i])):
                n_right[i][j][-1]=n_right[i][j][-1].replace(",","")
                n_right[i][j][-1]=n_right[i][j][-1].replace(".","")             
                n_right[i][j][-1]=n_right[i][j][-1].replace(":","")
                n_right[i][j][-1]=n_right[i][j][-1].replace("@","") 
        Mults=[]            
        Mults.append(multiplicities_extract(n_right))
        Mults.append(multiplicities_extract(n_left))             
        
    
        #Now go through multiplicities and detect abnormally high ones
        bigr_appended_right=[]
        bigr_appended_left=[]
        for i in range(len(Mults[0])):
            for j in range(len(Mults[0][i])):
                if Mults[0][i][j][1]>0.3*len(n_right[i]) and Mults[0][i][j][1]>min_occur:
                    print(i)
                    print(pronouns[i],Mults[0][i][j])
                    bigr_appended_right.append([pronouns[i][0]]+Mults[0][i][j][0])
        for i in range(len(Mults[1])):
            for j in range(len(Mults[1][i])):
                if Mults[1][i][j][1]>0.3*len(n_left[i]) and Mults[1][i][j][1]>min_occur:
                    print(i)
                    print(Mults[1][i][j],pronouns[i])   
                    bigr_appended_left.append(Mults[1][i][j][0]+[pronouns[i][0]])
        print(len(bigr_appended_left)+len(bigr_appended_right))
        
        #now remove pronouns that never appear on their own    
        for i in range(len(pronouns)):
            mults_take_right=[]
            for j in range(len(Mults[0][i])):
                mults_take_right.append(Mults[0][i][j][1])
            mults_take_left=[]
            for j in range(len(Mults[1][i])):
                mults_take_left.append(Mults[1][i][j][1])        
            if len(mults_take_right)>0 and len(mults_take_left)>0:
                if max(mults_take_right)>1 or max(mults_take_left)>1:
                    print(pronouns[i],mults_take_right,mults_take_left)
        
        #add popular pairs to the tokens_extended in place of the single words
        for term in bigr_appended_left+bigr_appended_right:
            num=0
            for count, sentence in enumerate(tokens_extended):
            
                k=sublist_consec(sentence,term)
                #print(k)
                if k:
                    sentence[k-1]=list_to_string(term)
                    lt=len(term)
                    del sentence[k:(k+lt-1)]
                    tokens_extended[count]=sentence
                    num=num+1
            if num>0:
                pronouns.append([list_to_string(term),num,"NNV"])
                
                
        token_file_plus="tokens_plus%s.csv" % n_iter
        token_path_plus=os.path.join(save_dir, token_file_plus)
        with open(token_path_plus, "w") as f:
            for s in tokens_extended:
                f.write(str(s) +"\n")             
                
        #recreate frequencies list
        print("Cleaning tokens")
        cleaned_extended = clean_sentences(tokens_extended, extra_stopwords)
 
        print("Getting word frequencies")
        frequencies_single = get_word_frequencies(cleaned_extended, extra_stopwords)
        vocab_size = len(frequencies)
        print("Unique words: " + str(vocab_size))
  return(tokens_extended,frequencies_single,pronouns)

 
if __name__ == '__main__':
  extra_stopwords = ["",".",":","Vol.","Ed.","ed.","eds.","eds","Diss","diss","vol.","PS","2000","2014","cf","oed", "del"]  
  
    
  userhome = os.path.expanduser('~')
    
  input_dir = userhome+"/Python Scripts/"
  save_dir = userhome+"/Python Scripts/Output/"
  if not os.path.exists(save_dir):
    os.makedirs(save_dir)
 
  
    
  print("Preprocessing raw data")
  raw_input_file = os.path.join(input_dir, "Vanin2.txt")
  filename = os.path.join(save_dir, "data.json")
  processed = try_load_or_process(filename, process_raw_data, raw_input_file, extra_stopwords)
  print("Unique sentences: " + str(len(processed)))
 
  print("Tokenizing sentences")
  filename = os.path.join(save_dir, "tokens.json")
  tokens = try_load_or_process(filename, tokenize_sentences, processed, extra_stopwords)
 
    

      
  print("Cleaning tokens")
  filename = os.path.join(save_dir, "cleaned.json")
  cleaned = try_load_or_process(filename, clean_sentences, tokens, extra_stopwords)
 
  print("Getting word frequencies")
  filename = os.path.join(save_dir, "frequencies.json")
  frequencies = try_load_or_process(filename, get_word_frequencies, cleaned, extra_stopwords)
  vocab_size = len(frequencies)
  print("Unique words: " + str(vocab_size))

  #try to group terms
  if group_on:
      print("Grouping")
      tokens,_,pronouns=nounlist_construct(frequencies,tokens,extra_stopwords)
      print("Cleaning grouped tokens")
      filename = os.path.join(save_dir, "cleaned_gr.json")
      cleaned = try_load_or_process(filename, clean_sentences, tokens, extra_stopwords)
     
      print("Getting group word frequencies")
      filename = os.path.join(save_dir, "frequencies_gr.json")
      frequencies = try_load_or_process(filename, get_word_frequencies, cleaned, extra_stopwords)
      vocab_size = len(frequencies)
      print("Unique words: " + str(vocab_size))      
     
  trimmed_vocab = []
  min_frequency_val = 0
  for item in frequencies:
    if item[1] >= min_frequency_val:
      trimmed_vocab.append(item[0])
  trimmed_vocab_size = len(trimmed_vocab)
  print("Trimmed vocab length: " + str(trimmed_vocab_size))
  filename = os.path.join(save_dir, "trimmed_vocab.json")
  save_json(trimmed_vocab, filename)
  
  
  #print
  print("Instantiating word2vec model")
  word2vec = get_word2vec(cleaned)
  vocab = word2vec.wv.vocab.keys()
  vocab_len = len(vocab)
  print("word2vec vocab contains " + str(vocab_len) + " items.")
  dim0 = word2vec.wv[list(vocab)[0]].shape[0]
  print("word2vec items have " + str(dim0) + " features.")
 
  print("Creating tensorboard embeddings")
  create_embeddings(word2vec)
 
  print("Calculating T-SNE for word2vec model")
  x_coords, y_coords, labels, arr = calculate_t_sne()
  
  
  plot_dir = os.path.join(save_dir, "plots")
  if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)
 
  num_similar = 15
  test_size = min(300,len(frequencies))
  test_words = []
  for item in frequencies[:test_size]:
    test_words.append(item[0])
    
  if group_on:
      test_words = []
      for item in pronouns[:test_size]:
          test_words.append(item[0])
    
  results = test_word2vec(test_words)
 
  big_plot_dir = os.path.join(save_dir, "big_plots")
  if not os.path.exists(big_plot_dir):
    os.makedirs(big_plot_dir)
  show_cluster_locations(results, labels, x_coords, y_coords)
#%%
#nouns  
  frequencies_single=copy.deepcopy(frequencies)
  frequencies_single=[list(elem) for elem in frequencies_single]
  
  parts_list=part_add(frequencies_single)
  
  
#%% 
#proper nouns


#%%
      
    #extract quotes
    
  word_limit=2
      
  quo=[]
  quo1=[]
  bra=[]
  for count,sentences in enumerate(processed):
    
        quo.append([])
    
        
        qsen=quotes_extract2(sentences,"‘","’")
        bsen=quotes_extract2(sentences,"(",")")
        
        for count2,quote in enumerate(qsen):
            qwords=quote.split(" ")
            if len(qwords)>word_limit:
                quo[count].append(quote)
                quo1.append(quote)
        bra.append(bsen)    
        if len(quo[count])>0:
            print(quo[count])
        if "creations of the twentieth century" in sentences:
            break
    
  for count,sentence in enumerate(processed):
        if len(quo[count])==0 and sentence[-1]==")":
            quo[count]=[sentence]
            
            #[re.sub("[\(].*?[\)]","",sentence)]
        if "creations of the twentieth century" in sentence:
            break
    
    #string the quotes and brackets together:
  braquo=[]        
  bradi=[]
  for count,sentence in enumerate(processed):    
        qplaces=[]
        qd={}
        for quote in quo[count]:
            
            quote_k = re.sub("[\(\)]", "", quote)
            
            sent_k = re.sub("[\(\)]", "", sentence)
            m=re.search(quote_k,sent_k)
            ms=m.start()
            qd[ms]=quote+" QQQ"
        for bracket in bra[count]:
            m=re.search(bracket,sentence)
            mb=m.start()
            qd[mb]=bracket+" BBB"
        
        
        for key in sorted(qd):
            qplaces.append(qd[key])
        #print(qd)    
        bradi.append(qd)
        
        braquo.append(qplaces)
        if "creations of the twentieth century" in sentence:
            break        
        
    #match up references and quotes:
  quo_all=list(flatten(braquo))
  for i in range(len(quo_all)):
        if "BBB" in quo_all[i]:
            if quo_all[i][0].isupper():
                quo_all[i]=re.sub("BBB","BRREF",quo_all[i])
            if quo_all[i][0:2]=="see":
                quo_all[i]=re.sub("BBB","BRREF",quo_all[i])            
            if quo_all[i][0].isdigit() and quo_all[i][1].isdigit() and quo_all[i][2].isdigit():
                if quo_all[i][3].isdigit():
                    quo_all[i]=re.sub("BBB","YR",quo_all[i])
                else:
                    quo_all[i]=re.sub("BBB","PGREF",quo_all[i])                
            if quo_all[i][0].isdigit() and quo_all[i][1].isdigit():
                if not quo_all[i][2].isdigit():
                    quo_all[i]=re.sub("BBB","PGREF",quo_all[i])
                    
    
  quo_all_m=[]
    
  for i in range(len(quo_all)):
        if "QQQ" in quo_all[i]:
            wcount=len(quo_all[i].split(" "))-1
            
            ind=0
            j=0
            while(1):
               j=j+1
               if "BRREF" in quo_all[i+j] or "PGREF" in quo_all[i+j]:
                   if "BRREF" in quo_all[i+j]:
                       refkey=quo_all[i+j].split(" ")[0]
                       
                       if refkey=="That":
                           refkey="McCulloch"
                       if refkey=="Ainur":
                           refkey="LT"
                   #elif "PGRREF" in quo_all[i+j]:
                       
                    
                   else:
                       refkey="NONE"
                   
                   quo_all_m.append([quo_all[i],quo_all[i+j],refkey,wcount])
                   break
    
    
  identifiers=[]
  for i in range(len(quo_all_m)):
        identifiers.append(quo_all_m[i][2])
        
  identifiers=list(set(identifiers))
  wcounts=[]
    
  for i in range(len(identifiers)):
        wcounts.append(0)
        print(identifiers[i])
        for j in range(len(quo_all_m)):
            if quo_all_m[j][2]==identifiers[i]:
                if identifiers[i]=="Letters,":
                    print(quo_all_m[j])
                wcounts[len(wcounts)-1]=wcounts[len(wcounts)-1]+quo_all_m[j][3]
                
            
  for i in range(len(identifiers)):
        print([identifiers[i]],wcounts[i])      
    
    #classify according to the reference key
               
                


                
#%%
  #bigrams
  all_stopwords = load_json("stopwords-iso.json")+extra_stopwords
  bigrams,counts_all=bigrams_find(frequencies,tokens,all_stopwords,fr_limit=0)
  
  
  bigrams_by_freq=[]
  for i in range(100):
      bigrams_by_freq.append([])
  
  
  limit=5
  for c,count in enumerate(counts_all,0):   
      for i in range(len(count)):
          bigrams_by_freq[count[i]].append(bigrams[c][i])
          if count[i]>limit:
              print(bigrams[c][i])
              print(count[i])
             
  for i in range(len(bigrams_by_freq)):
      if len(bigrams_by_freq[i])>0:
          bigrams_by_freq[i]=np.unique(bigrams_by_freq[i]).tolist()
          
          
  for i in range(len(bigrams_by_freq)):
      if len(bigrams_by_freq[i])>0:
          print(str(i)+"\t"+str(len(bigrams_by_freq[i])))
  #for test
#  frequencies_test=[frequencies[101]]
 # bigrams_test,counts=bigrams_find(frequencies_test,tokens,all_stopwords)
  
  #frequencies_test=[frequencies[9000]]
  #bigrams_test,counts=bigrams_find(frequencies_test,tokens,all_stopwords)
  
  
  #sanity check

          
      
      
  
  
  #rerun with the bigrams as tokens
  #find bigrams in each para separately
  bigrams_para=[]
  counts=[]
  for para in tokens:
      bgs_new,_=bigrams_find(frequencies,[para],all_stopwords,fr_limit=0)
      bigrams_para=bigrams_para+bgs_new
  
  
  nltk.download('averaged_perceptron_tagger')
  bigram_strings=[]  
  for count,bgpara in enumerate(bigrams_para):
      bgpara_cleaned=bigrams_adj_clean(bgpara)
      bigram_strings.append([])
      if len(bgpara_cleaned)==0:
          continue

      for bigram in bgpara_cleaned:
          bigram_strings[count].append(list_to_string(bigram))
    
    
  print("Getting word frequencies")
  filename = os.path.join(save_dir, "frequencies_b.json")
  wvfile="bigrams_vectors.w2v"
  vocab_vectors="vocab_vectors_b.npy"
  xcorfile="x_coords_b.npy"
  ycorfile="y_coords_b.npy"
  plotdir="plots_bigrams1"
  assoc="associations_b.csv"
  labelsfile="labels_b.json"
  frequencies = try_load_or_process(filename, get_word_frequencies, bigram_strings, extra_stopwords, must_process=1)
  vocab_size = len(frequencies)
  print("Unique words: " + str(vocab_size))
 
 
  trimmed_vocab = []
  min_frequency_val = 2
  for item in frequencies:
    if item[1] >= min_frequency_val:
      trimmed_vocab.append(item[0])
  trimmed_vocab_size = len(trimmed_vocab)
  print("Trimmed vocab length: " + str(trimmed_vocab_size))
  filename = os.path.join(save_dir, "trimmed_vocab.json")
  save_json(trimmed_vocab, filename)
  
  
  #print
  print("Instantiating word2vec model")
  word2vec = get_word2vec(bigram_strings)
  vocab = word2vec.wv.vocab.keys()
  vocab_len = len(vocab)
  print("word2vec vocab contains " + str(vocab_len) + " items.")
  dim0 = word2vec.wv[list(vocab)[0]].shape[0]
  print("word2vec items have " + str(dim0) + " features.")
 
  print("Creating tensorboard embeddings")
  create_embeddings(word2vec)
 
  print("Calculating T-SNE for word2vec model")
  x_coords, y_coords, labels, arr = calculate_t_sne()
  
  
  plot_dir = os.path.join(save_dir, plotdir)
  if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)
 
  num_similar = 40
  test_size = min(100,len(frequencies))
  test_words = []
  for item in frequencies[:test_size]:
    test_words.append(item[0])
  results = test_word2vec(test_words)
 
  big_plot_dir = os.path.join(save_dir, "big_plots")
  if not os.path.exists(big_plot_dir):
    os.makedirs(big_plot_dir)
  show_cluster_locations(results, labels, x_coords, y_coords)
