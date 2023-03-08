from math import log, sqrt
from collections import defaultdict

# using the lnc.ltc weighting scheme and the example from lecture 21

# instead of comparing tf-idf for any doc containing at least one query term, should set separate
# function to find docs that contain more than one (see lecture 22)

def compare_tf_idf(query: str, union_docs: list('Postings'), doc_vec_sizes: dict(), total_doc_count: int, search_num: int):
    query_tokens = set(query.split())
    
    query_weights = defaultdict(int)
    scores = defaultdict(int)
    
    for token in query_tokens:
        q_tf_wt = 1 + log(query.count(token), base = 10)
        q_idf = log((total_doc_count / len(main_index[token])), base = 10) # change to file seeking
        
        query_wt = q_tf_wt * q_idf
        query_weights[token] = query_wt
        
        for posting in union_docs:
            scores[posting.get_docID()] = query_wt * posting.get_tf()
             
    query_vec_size = sqrt(sum([w**2 for w in query_weights])) # used in cosine normalization
    
    
    for docID in scores:
        scores[docID] = scores[docID] / (query_vec_size * doc_vec_sizes[docID])
    
    return scores.values().sort(scores[1], reverse = True)[0:search_num]