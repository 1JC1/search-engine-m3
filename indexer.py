import json, os, re, sys, bisect, psutil, math
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from Posting import Posting
from string import ascii_lowercase

"""
psutil.virtual_memory()[2]
"""

main_index = dict()
disk_index = dict()
index_of_index = dict()
url_index = dict()

newpath = "file_index"

if not os.path.exists(newpath):
    os.makedirs(newpath)

os.chdir(newpath)

for char in ascii_lowercase:
    f = open(f"{char}.txt", "W+")
    disk_index[char] = f
    
f = open(f"num.txt", "w+")
disk_index[char] = f
    
os.chdir("../")

def dump():
    global main_index
    global disk_index
    
    sorted_dict_list = sorted(main_index.keys())
    curr = sorted_dict_list[0][0]
    
    if curr not in ascii_lowercase:
        curr = "num"
    
    line = disk_index[curr].readline()
    p = 0

    newf = open(f"new_{curr}.txt", "w")

    while line != "" or p < len(sorted_dict_list):
        
        if line == "" and p < len(sorted_dict_list):
            main_token = sorted_dict_list[p]
            main_postings = main_index[main_token]
            newf.write(f"{main_token}|{main_postings}\n")
            p += 1
            if p == len(sorted_dict_list) or sorted_dict_list[p][0] != curr:
                newf.close()
                disk_index[curr].close()
                os.remove(f"{curr}.txt")
                os.rename(f"new_{curr}.txt", f"{curr}.txt")
                disk_index[curr] = open(f"{curr}.txt", "r")
                if p < len(sorted_dict_list) and sorted_dict_list[p][0] != curr:
                    curr = sorted_dict_list[p][0]
                    
                    if curr not in ascii_lowercase:
                        curr = "num"
                    
                    newf = open(f"new_{curr}.txt", "w")
            
        elif line != "" and p == len(sorted_dict_list):
            line_info = line.strip().split("|")
            disk_token = line_info[0]
            disk_postings = eval(line_info[1])
            newf.write(f"{disk_token}|{disk_postings}\n")
            line = disk_index[curr].readline()
            
        elif line != "" and p < len(sorted_dict_list):
            main_token = sorted_dict_list[p]
            main_postings = main_index[main_token]
            
            line_info = line.strip().split("|")
            disk_token = line_info[0]
            disk_postings = eval(line_info[1])
            
            if main_token == disk_token:
                merged_list = sorted(disk_postings + main_postings)
                newf.write(f"{main_token}|{merged_list}\n")
                p += 1
                if p == len(sorted_dict_list) or sorted_dict_list[p][0] != curr:
                    newf.close()
                    disk_index[curr].close()
                    os.remove(f"{curr}.txt")
                    os.rename(f"new_{curr}.txt", f"{curr}.txt")
                    disk_index[curr] = open(f"{curr}.txt", "r")
                    if p < len(sorted_dict_list) and sorted_dict_list[p][0] != curr:
                        curr = sorted_dict_list[p][0]
                        
                        if curr not in ascii_lowercase:
                            curr = "num"
                        
                        newf = open(f"new_{curr}.txt", "w")
                line = disk_index[curr].readline()
                
            elif main_token < disk_token:
                newf.write(f"{main_token}|{main_postings}\n")
                p += 1
                if p == len(sorted_dict_list) or sorted_dict_list[p][0] != curr:
                    newf.close()
                    disk_index[curr].close()
                    os.remove(f"{curr}.txt")
                    os.rename(f"new_{curr}.txt", f"{curr}.txt")
                    disk_index[curr] = open(f"{curr}.txt", "r")
                    if p < len(sorted_dict_list) and sorted_dict_list[p][0] != curr:
                        curr = sorted_dict_list[p][0]
                        
                        if curr not in ascii_lowercase:
                            curr = "num"
                        
                        newf = open(f"new_{curr}.txt", "w")
                        
            elif main_token > disk_token:
                newf.write(f"{disk_token}|{disk_postings}\n")
                line = disk_index[curr].readline()
    
    main_index = dict()

def create_index_of_index():
    global index_of_index
    
    for char in ascii_lowercase:
        line = disk_index[char].readline()
        pos = 0
        
        while line != "":
            line_info = line.strip().split("|")
            token = line_info[0]
            index_of_index[token] = pos
            pos += len(line)
            line = disk_index[char].readline()

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
                        tokens = word_tokenize(soup.get_text())
                    
                        # tokenizing alphanumerically
                        for token in tokens:
                            alphanum = re.sub(r'[^a-zA-Z0-9]', '', token)
                            
                            # only allowing alphanumeric characters to be stemmed
                            if len(alphanum) > 0:
                                stem = stemmer.stem(alphanum)
                                
                                # print(f'Token: {token}, Stem: {stem}')
                                
                                # creating a Posting object to easily access docID and frequencies of tokens
                                # & putting the Posting objects into the main_index
                                if stem not in file_index:
                                    file_index[stem] = Posting(docID, stem)
                                    
                                file_index[stem].increment_freq()
                                file_index[stem].add_position(wordPosition)
                                
                                wordPosition += 1
                
        
                    # adding docIDs, frequencies, and URLs to dict and defaultdict
                    for stem, post in file_index.items():
                        if stem not in main_index:
                            main_index[stem] = []
                        post.set_tfWeight(1 + math.log10(post.get_freq()))
                        bisect.insort(main_index[stem], post)
                                
                    url_index[docID] = data['url']
                        
                    docID += 1
                    
                    if sys.getsizeof(main_index) >= (psutil.virtual_memory()[0] / 2) or psutil.virtual_memory()[2] >= 100:
                        dump()

            print(f'Directory {dir} done\n')
            # break

    # ensuring main_index.json gets dumped in inverted-index-m1 directory instead of DEV 
    os.chdir("../inverted-index-m1")
    
    # dumping main_index into a json
    # with open("main_index.json", 'w') as f:
    #     json.dump(main_index, f, default=default)
    #     print("File index made")
    dump()
    
    # with open("url_index.json", "w") as f:
    #     json.dump(url_index, f, default=default)
    #     print("URL index made")
    
    # print(f"Number of documents: {docID + 1}")
    # print(f"Number of tokens: {len(main_index)}")
    # print(f"Size of index: {sys.getsizeof(main_index)}")

    # print('main index:')
    # print(main_index)
    # print('url index')
    # print(url_index)  