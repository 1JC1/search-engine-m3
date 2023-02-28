from search import search
from indexer import indexer

if __name__ == "__main__":

    indexer()

    while True:
        query = input("What would you like to search? Press Q to quit.\n")
        
        if query.lower() == 'q':
            break

        for url in search(query.strip()):
            print(url)
        '''
              print(f"Searching for query {query}... ")
        for count, result in enumerate(result_list, start=1):
            print(f"{count} | {url_index[result.get_docID()]:100} | {result.get_freq()}")  
        '''        

        
        print()
