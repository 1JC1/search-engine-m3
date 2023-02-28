import json, os, re, sys, heapq
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from Posting import Posting
from indexer import indexer, main_index, url_index
from collections import defaultdict

def process_query(query: str):
    # add stopword removal / recognition
    tokens_to_search = set()
    
    stemmer = SnowballStemmer("english", ignore_stopwords=True)
    
    for token in word_tokenize(query):
        alphanum = re.sub(r'[^a-zA-Z0-9]', '', token)
        
        if len(alphanum) > 0:
            stem = stemmer.stem(alphanum)
            tokens_to_search.add(stem)
    
    return tokens_to_search

def intersect(list_1, list_2, included: set):
    answer = []
    p1 = 0
    p2 = 0
    
    while p1 < len(list_1) and p2 < len(list_2):

        if list_1[p1].get_docID() == list_2[p2].get_docID():

            if (list_1[p1] not in included):
                answer.append(list_1[p1])
                included.add(list_1[p1])

            if (list_2[p2] not in included):
                answer.append(list_2[p2])
                included.add(list_2[p2])

            p1 += 1
            p2 += 1

        elif list_1[p1] < list_2[p2]:
            p1 += 1

        else:
            p2 += 1
    
    return answer


def simple_rank(result_list):
    rel_score = defaultdict(float)

    for posting in result_list:
        rel_score[posting.get_docID()] += posting.get_freq()

    return sorted(rel_score, key=lambda x : rel_score[x], reverse=True)[0:5] 
    

    
def search(query: str):

    tokens = process_query(query)

    token_list = [t for t in tokens if t in main_index]
    token_list.sort(key=lambda t: len(main_index[t]))
    
    result_list = []
    included = set()
    
    if len(token_list) > 1:
        result_list = intersect(main_index[token_list[0]], main_index[token_list[1]], included)
        
        for i in range(2,len(token_list)):
            result_list = intersect(result_list, main_index[token_list[i]], included)
        
    elif len(token_list) == 1:
        result_list = main_index[token_list[0]]


    return [url_index[id] for id in simple_rank(result_list)]

