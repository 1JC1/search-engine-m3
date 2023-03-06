from math import log
from collections import defaultdict

# weighted term frequency (tf) stored in Posting objects
# document frequency (df) is length of Posting list
# term frequency (tf) is 1 + log(main_index[term][i].get_freq(), base = 10

def calc_tf_idf(total_doc_count: int, df: int, tf: int):
    # Calculates tf-idf score for individual token 
    idf = log(total_doc_count / df, base = 10) # log10(N/df)

    return tf * idf 

# note: have to account for repeating tokens (ex. ics ics)
def compare_tf_idf(query_tokens: list[str], total_doc_count: int, search_num):
    scores = defaultdict(int)
    
    for token in query_tokens:
        token_postings = main_index[token]
        query_weight = calc_tf_idf(total_doc_count, len(token_postings), 1 + log(query_tokens.count(token)))
        
        for posting in token_postings:
            doc_weight = calc_tf_idf(total_doc_count, len(token_postings), posting.get_tf()) 
            # replace get_tf with correct method name; maybe change to just tf and cosine normalization
            scores[posting.get_docID()] += query_weight * doc_weight
            
    for docID in scores:
        scores[docID] = scores[docID] # / length[docID] # change once we confirm what length is
    
    return scores.values().sort(scores[1])[0:search_num] # assuming we want smaller angles