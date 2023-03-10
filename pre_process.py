from math import log, sqrt
from collections import defaultdict

# using the lnc.ltc weighting scheme and the example from lecture 21

# instead of comparing tf-idf for any doc containing at least one query term, should set separate
# function to find docs that contain more than one (see lecture 22)

def compare_tf_idf(query: str, union_docs: list('Postings'), main_index, search_num: int):
    # Compares tf-idf scores between query and document terms using cosine similarity and returns top K docIDs with their
    # scores, where K is specified by the search_num argument.
    
    query_weights = defaultdict(int)
    scores = defaultdict(int)
    
    query_tokens = set(query.split())
    
    for token in query_tokens:
        q_tf_wt = 1 + log(query.count(token), base = 10) # weighted tf for query
        q_idf = log((docID / len(main_index[token])), base = 10) # idf for query # change main_index to file seeking? or other structure
        
        query_wt = q_tf_wt * q_idf # non-normalized query weight
        query_weights[token] = query_wt
        
        for posting in union_docs:
            scores[posting.get_docID()] = query_wt * posting.get_tf()
             
    query_vec_size = sqrt(sum([w**2 for w in query_weights]))
    
    for dID in scores: # doing cosine normalization on all query-document scores
        scores[dID] = scores[dID] / (query_vec_size * url_index[dID][2])
    
    return scores.values().sort(scores[1], reverse = True)[0:search_num] # return top K documents
