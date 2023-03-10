import json, os, re, sys, bisect
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from Posting import Posting
from collections import defaultdict

main_index = dict()
url_index = dict()
anchor_dict = defaultdict(list)
stemmer = SnowballStemmer("english", ignore_stopwords=True)

def default(obj):
    '''Encoder object to serialize Postings class as a JSON object'''
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

def tokenize(soup, token_nested_dict, count):
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
            token_nested_dict[stem] += count

def tags(soup, token_nested_dict):
    '''Searching for tags in text, creating a list of the tags, and calling tokenize() 
    to categorize tokenize each tag into a dict'''
    #title --> used to display in ui

    for title in soup.findAll('title'):
        tokenize(title, token_nested_dict, 10)
    #h1, h2/h3, h4/h5/h6
    for num in range(0, 6):
        for head in soup.findAll('h' + str(num)):
            tokenize(head, token_nested_dict, 10 - num)
    #strong
    for strong in soup.findAll('strong'):
        tokenize(strong, token_nested_dict, 10)
    #bold
    for bolded in soup.findAll('bold'):
        tokenize(bolded, token_nested_dict, 3)
    #emphasized
    for em in soup.findAll('em'):
        tokenize(em, token_nested_dict, 5)
    #italics
    for italics in soup.findAll('i'):
        tokenize(italics, token_nested_dict, 3)
    #anchor tags
    for anchor in soup.findAll('a'):

        if anchor.get('title'):
            for token in word_tokenize(anchor.get('title')):
                alphanum = re.sub(r'[^a-zA-Z0-9]', '', token)
                if len(alphanum) > 0:
                    stem = stemmer.stem(alphanum)
                    anchor_dict[stem].append(anchor.get('href'))


    
def indexer():
    '''Read through JSON file, create docID, parse content with listed encoding, tokenize,
        stemming and other language processing, add doc as postings to inverted index (dictionary) '''
    global main_index
    global url_index
    docID = 0

    # using Porter2 stemmer to stem all english words except stop words
    

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
                    token_nested_dict = defaultdict(int)
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
                    
                #print("Anchor Dict:/n", anchor_dict)
            print(f'Directory {dir} done\n')
            # break

    # ensuring main_index.json gets dumped in inverted-index-m1 directory instead of DEV 
    print(anchor_dict)
    os.chdir("../inverted-index-m1")
    
    # dumping main_index into a json
    with open("main_index.json", 'w') as f:
        json.dump(main_index, f, default=default)
        print("File index made")
    
    with open("url_index.json", "w") as f:
        json.dump(url_index, f, default=default)
        print("URL index made")

if __name__ == "__main__":
    indexer()