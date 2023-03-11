import re, math
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from Posting import Posting
from indexer import main_index, index_of_index, disk_index
from collections import defaultdict
from string import ascii_lowercase

anchor_dict = defaultdict(int)
url_index = dict()
totalDocs = 0


def init_url_anchor(inUrlIndex, inAnchorDict):
    global anchor_dict
    global url_index
    global totalDocs
    url_index = inUrlIndex
    anchor_dict = inAnchorDict
    totalDocs = len(url_index)


def process_query(query: str):
    # add stopword removal / recognition
    tokens_to_search = defaultdict(int)
    
    stemmer = SnowballStemmer("english", ignore_stopwords=True)
    
    for token in word_tokenize(query):
        alphanum = re.sub(r'[^a-zA-Z0-9]', '', token)
        
        if len(alphanum) > 0:
            stem = stemmer.stem(alphanum)

            if stem in index_of_index:

                tokens_to_search[stem] += 1

    
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
    

def repopulate_main(tokens):
    global main_index
    global disk_index
    
    for tok in tokens:
        if tok[0] not in ascii_lowercase:
            disk_index["num"].seek(index_of_index[tok])
            line_info = disk_index["num"].readline().strip().split("|")
            main_index[tok] = eval(line_info[1])
            disk_index["num"].seek(0)
        else:
            disk_index[tok[0]].seek(index_of_index[tok])
            line_info = disk_index[tok[0]].readline().strip().split("|")
            main_index[tok] = eval(line_info[1])
            disk_index[tok[0]].seek(0)


def compare_tf_idf(query_tokens: defaultdict(int), union_docs: list('Postings'), search_num: int):
    # Compares tf-idf scores between query and document terms using cosine similarity and returns top K docIDs with their
    # scores, where K is specified by the search_num argument.
    
    query_weights = defaultdict(int)
    scores = defaultdict(int)
    
    for token in query_tokens:
        q_tf_wt = 1 + math.log10(query_tokens[token]) # weighted tf for query
        q_idf = math.log10(( totalDocs / len(main_index[token]))) # idf for query # change main_index to file seeking? or other structure
        
        query_wt = q_tf_wt * q_idf # non-normalized query weight
        query_weights[token] = query_wt
        
        for posting in union_docs:
            scores[posting.get_docID()] += query_wt * posting.get_tfWeight()
             
    query_vec_size = math.sqrt(sum([w**2 for w in query_weights.values()]))
 
    for dID in scores: # doing cosine normalization on all query-document scores
        scores[dID] = scores[dID] / (query_vec_size * url_index[dID][2])


    return sorted(scores, key=lambda x : scores[x], reverse=True)[0:search_num]
    



def search(query: str):

    token_dict = process_query(query)
    token_list = list(token_dict.keys())

    repopulate_main(token_list)

    posting_list = []
    included = set()
    
    if len(token_list) > 1:
        posting_list = intersect(main_index[token_list[0]], main_index[token_list[1]], included)
        
        for i in range(2,len(token_list)):
            posting_list = intersect(posting_list, main_index[token_list[i]], included)
        
    elif len(token_list) == 1:
        posting_list = main_index[token_list[0]]
    

    topDocs = compare_tf_idf(token_dict, posting_list, 10)

    return [url_index[id][0] for id in topDocs]
