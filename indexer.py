import json, os, re, sys, bisect
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from Posting import Posting
import defaultdict

main_index = dict()
url_index = dict()
token_nested_dict = dict(defaultdict(int))

def default(obj):
    '''Encoder object to serialize Postings class as a JSON object'''
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

def tokenize(soup, tag):
    '''Used to tokenize and stem HTML tags for search revelance; puts relevant tokens into a 
    dictionary: token_nested_dict'''
    tokens = word_tokenize(soup.get_text())
    # tokenizing alphanumerically
    for token in tokens:
        alphanum = re.sub(r'[^a-zA-Z0-9]', '', token)
        
        # only allowing alphanumeric characters to be stemmed
        if len(alphanum) > 0:
            stem = stemmer.stem(alphanum)
            token_nested_dict[token][tag] = +1

def tags(soup):
    '''Searching for tags in text and calling tokenize() to categorize tokens into a dict'''
    #title --> used to display in ui
    for title in soup.findall('title'):
        tokenize(title, 'title')
    #h1, h2/h3, h4/h5/h6
    for num in str(range (1, 7)):
        for head in soup.findall('h' + num):
            tokenize(head, 'h' + num)
    #strong
    for strong in soup.findall('strong'):
        tokenize(strong, 'strong')
    #bold
    for bolded in soup.findall('bold'):
        tokenize(bolded, 'bold')
    
    #emphasized
    for em in soup.findall('em'):
        tokenize(em, 'em')
    
def indexer():
    '''Read through JSON file, create docID, parse content with listed encoding, tokenize,
        stemming and other language processing, add doc as postings to inverted index (dictionary) '''
    global main_index
    global url_index
    docID = 0

    # using Porter2 stemmer to stem all english words except stop words
    stemmer = SnowballStemmer("english", ignore_stopwords=True)

    # changing into the DEV directory and opening it
    os.chdir("../DEV")
    for dir in os.listdir():
        if dir != '.DS_Store':
            print(f'Directory {dir} started')
            
            # opening the subdirectories in dev directory
            for file in os.listdir(dir):
                
                # opening each file in subdirectories and parsing data
                if os.path.splitext(file)[1] == '.json':
                    file_index = dict()
                    wordPosition = 0
                    
                    with open(dir + '/' + file) as f:

                        # try/except allows us to view any errors that may occur and continue the code
                        try:
                            data = json.load(f)
                        except Exception as e:
                            print(f"Directory: {dir}, File: {file}")
                            print(f"Error: {e}")    # prints the type of error displayed
                            continue

                        # using BeautifulSoup to parse data
                        soup = BeautifulSoup(data['content'].encode(data['encoding']), 'lxml', from_encoding = data['encoding'])

                        #finding tags in html
                        tags(soup)
                        tokens = word_tokenize(soup.get_text())
                        
                        # tokenizing alphanumerically
                        for token in tokens:
                            alphanum = re.sub(r'[^a-zA-Z0-9]', '', token)
                            
                            # only allowing alphanumeric characters to be stemmed
                            if len(alphanum) > 0:
                                stem = stemmer.stem(alphanum)
                                
                                
                                # creating a Posting object to easily access docID and frequencies of tokens
                                # & putting the Posting objects into the main_index
                                if stem not in file_index:
                                    file_index[stem] = Posting(docID, stem)
                                else:
                                    file_index[stem].increment_freq()
                                    file_index[stem].add_position(wordPosition)
                                
                                wordPosition += 1
                
        
                    # adding docIDs, frequencies, and URLs to dict and defaultdict
                    for stem, post in file_index.items():
                        if stem not in main_index:
                            main_index[stem] = []
                        bisect.insort(main_index[stem], post)
                                
                    url_index[docID] = data['url']
                        
                    docID += 1

            print(f'Directory {dir} done\n')
            # break

    # ensuring main_index.json gets dumped in inverted-index-m1 directory instead of DEV 
    os.chdir("../inverted-index-m1")
    
    # dumping main_index into a json
    with open("main_index.json", 'w') as f:
        json.dump(main_index, f, default=default)
        print("File index made")
    
    with open("url_index.json", "w") as f:
        json.dump(url_index, f, default=default)
        print("URL index made")
