from search import search, init_url_anchor
from indexer import indexer, create_index, create_index_of_index, open_files, close_files, load_json
from collections import defaultdict
from timeit import default_timer as timer


if __name__ == "__main__":

    try:
        createIndex = False #in case we do not want to create index from scratch
        
        if createIndex:
            create_index()
            url_index, anchor_dict = indexer()
        else:
            open_files() #if we dont create index from scratch, we still want to open all of the files 
            url_index, anchor_dict = load_json()

        create_index_of_index()

        init_url_anchor(url_index, anchor_dict)


        while True:
            query = input("What would you like to search? Press Q to quit.\n")
            
            if query.lower() == 'q':
                break
            
            search_start = timer()
            search_results = search(query.strip())
            search_end = timer()
            
            for url in search_results:
                print(url)
      
            print(f"\Search took {search_end - search_start} sec")

    finally:
        close_files()

