import json, os, re, sys, bisect
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from Posting import Posting
from collections import defaultdict

main_index = dict()
url_index = dict()
anchor_dict = dict()

def default(obj):
    '''Encoder object to serialize Postings class as a JSON object'''
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

def tokenize(soup, tag, token_nested_dict, count):
    '''Used to tokenize and stem HTML tags for search revelance; puts relevant tokens into a 
    dictionary: token_nested_dict'''
    # getting text to make the tag readable 
    tokens = word_tokenize(soup.get_text())
    # tokenizing alphanumerically
    for token in tokens:
        alphanum = re.sub(r'[^a-zA-Z0-9]', '', token)
        
        # only allowing alphanumeric characters to be stemmed
        if len(alphanum) > 0:
            stem = stemmer.stem(alphanum)
            token_nested_dict[token][tag] += count

def tags(soup, token_nested_dict):
    '''Searching for tags in text, creating a list of the tags, and calling tokenize() 
    to categorize tokenize each tag into a dict'''
    #title --> used to display in ui
    for title in soup.findall('title'):
        tokenize(title, 'title', token_nested_dict, 6)
    #h1, h2/h3, h4/h5/h6
    for num in str(range (0, 6)):
        for head in soup.findall('h' + num):
            tokenize(head, 'h' + str(num + 1), token_nested_dict, 6 - num)
    #strong
    for strong in soup.findall('strong'):
        tokenize(strong, 'strong', token_nested_dict, 6)
    #bold
    for bolded in soup.findall('bold'):
        tokenize(bolded, 'bold', token_nested_dict, 4)
    #emphasized
    for em in soup.findall('em'):
        tokenize(em, 'em', token_nested_dict, 2)
    #italics
    for italics in soup.findall('i'):
        tokenize(italics, 'i', token_nested_dict, 2)
    #anchor tags
    for anchor in soup.findall('a'): 
        tokenize(anchor, 'a', token_nested_dict, 3)
        anchor_dict[anchor.get('href')]
    
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
                    token_nested_dict = dict(defaultdict(int))
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

                        # finding tags in html
                        tags(soup, token_nested_dict)
                        tokens = word_tokenize(soup.get_text())
                        
                        print("token nested dict:/n", token_nested_dict)
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
                    
                print("Anchor Dict:/n", anchor_dict)
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

