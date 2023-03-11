from search import search
from indexer import indexer, create_index, create_index_of_index, open_files, close_files, load_json, url_index
import time 

if __name__ == "__main__":

    try:
        createIndex = False #in case we do not want to create index from scratch
        
        if createIndex:
            create_index()
            indexer()
        else:
            open_files() #if we dont create index from scratch, we still want to open all of the files 
            load_json()

        create_index_of_index()

        while True:
            query = input("What would you like to search? Press Q to quit.\n")
            
            if query.lower() == 'q':
                break

            for url in search(query.strip()):
                print(url)
      
            print()

    finally:
        close_files()

