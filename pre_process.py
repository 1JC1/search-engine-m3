from math import log, sqrt
from collections import defaultdict

# using the lnc.ltc weighting scheme and the example from lecture 21

# instead of comparing tf-idf for any doc containing at least one query term, should set separate
# function to find docs that contain more than one (see lecture 22)

def compare_tf_idf(query: str, total_doc_count: int):
    query_tokens = set(query.split())
    
    query_weights = defaultdict(int)
    scores = defaultdict(int)
    
    for token in query_tokens:
        token_postings = main_index[token] # change to file seeking
        
        q_tf_wt = 1 + log(query.count(token), base = 10)
        q_idf = log((total_doc_count / len(token_postings)), base = 10)
        
        query_wt = q_tf_wt * q_idf
        query_weights[token] = query_wt
        
    query_vector_size = sqrt(sum([w**2 for w in query_weights])) # used in cosine normalization
    
    for token in query_weights:
        query_weights[token] = query_weights[token] / query_vector_size
    
    for token in query_tokens:
        for posting in main_index[token]:
            doc_weight = posting.get_tf() / doc_vector_size # replace with actual way to get document vector size
            scores[posting.get_docID()] += query_weights[token] * doc_weight
        
    
    return scores.values().sort(scores[1], reverse = True)[0:search_num]