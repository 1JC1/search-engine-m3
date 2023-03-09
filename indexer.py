import json, os, re, sys, bisect, psutil, math
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from Posting import Posting
from collections import OrderedDict, defaultdict
from string import ascii_lowercase
import hashlib

#GLOBALS
letter_list = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z', 'num']
main_index = dict()
disk_index = dict() #has the open files to each of the letter.txt's
index_of_index = dict() #stores all the words and its position in the disk_index
url_index = dict()
newpath = "file_index"


def close_files():
    for f in disk_index.values():
        f.close()


def open_files():
    os.chdir(newpath)
    for char in letter_list:
        f = open(f"{char}.txt", "r") #r for reading only, wont have to write since this only gets called for 
        disk_index[char] = f
    os.chdir("../")


def create_index():
    global disk_index

    #if file_index path does not exist, create it
    if not os.path.exists(newpath): 
        os.makedirs(newpath)

    #change directory into new path in order to create a-z.txt's
    os.chdir(newpath)

    for char in letter_list:
        f = open(f"{char}.txt", "w+") #w+ allows for both read and write and also the text is overritten and deleted from existing file
        disk_index[char] = f
        
    os.chdir("../")


def create_index_of_index():
    global index_of_index 
    
    for char in letter_list: #looping through every letter 

        #start position at 0 and for every token, keep track of its positon in the disk_index file
        #index_of_index key = token, value = position, for O(1) seek operation later on
        disk_index[char].seek(0)
        line = disk_index[char].readline()
        pos = 0
        
        while line:
            line_info = line.strip().split("|")
            token = line_info[0]
            index_of_index[token] = pos
            pos += len(line)
            line = disk_index[char].readline()


def union_postings(postings1, postings2):
    answer = []
    p1 = 0
    p2 = 0
    
    while p1 < len(postings1) and p2 < len(postings2):

        if postings1[p1].get_docID() < postings2[p2].get_docID():
            answer.append(postings1[p1])
            p1+=1
        elif postings1[p1].get_docID() > postings2[p2].get_docID():
            answer.append(postings2[p2])
            p2+=1
        else:
            answer.append(postings2[p2])
            p1+=1
            p2+=1

    if p1 < len(postings1):
        answer.extend(postings1[p1:])   
    elif p2 < len(postings2):
        answer.extend(postings2[p2:])

    return answer



def merge(main_tokens, disk_file, merged_file):

    p = 0
    line = disk_file.readline()
    if line:
        disk_line_info = line.strip().split("|")
        disk_token = disk_line_info[0]
        disk_postings = eval(disk_line_info[1])

    while p < len(main_tokens) and line:

        if main_tokens[p] < disk_token:
            merged_file.write(f"{main_tokens[p]}|{main_index[main_tokens[p]]}\n")
            p+=1

        elif main_tokens[p] > disk_token:
            merged_file.write(f"{disk_token}|{disk_postings}")
            line = disk_file.readline()
            if line:
                disk_line_info = line.strip().split("|")
                disk_token = disk_line_info[0]
                disk_postings = eval(disk_line_info[1])

        else:

            postings = union_postings(main_index[main_tokens[p]], disk_postings)
            merged_file.write(f"{disk_token}|{postings}")

    if p < len(main_tokens):
        for tok in main_tokens[p:]:
            merged_file.write(f"{tok}|{main_index[tok]}\n")

    elif line:
        while line:
            merged_file.write(f"{disk_token}|{disk_postings}")
            line = disk_file.readline()
            if line:
                disk_line_info = line.strip().split("|")
                disk_token = disk_line_info[0]
                disk_postings = eval(disk_line_info[1])



def dump():
    global main_index
    global disk_index
    
    os.chdir(newpath)

    main_token_bins = defaultdict(list)
    for tok in sorted(main_index.keys()):
        if tok[0] not in ascii_lowercase:
            main_token_bins['num'].append(tok)
        else:
            main_token_bins[tok[0]].append(tok)
    
    #main_token_bins have the tokens in their respective letter, also in alphabetical order

    for curr, curr_token_list in main_token_bins.items():
        #curr is the current letter and curr_token_list is the tokens from main_index for that
        #now we merge disk_index[curr] and curr_token_list in merge() function

        newf = open(f"new_{curr}.txt", "w")

        merge(curr_token_list, disk_index[curr], newf)

        newf.close()

        os.remove(f"{curr}.txt")
        os.rename(f"new_{curr}.txt", f"{curr}.txt")

    
    main_index.clear()
    os.chdir("../")


def simhashSimilarity(simhash_info: dict[str: list[int, str]], url: str) -> tuple[int, str or None]:

    simhash = [0]*128
    for i in range(128):
        for weight, hash_val in simhash_info.values():
            if hash_val[i] == '1':
                simhash[i] += weight
            else:
                simhash[i] -= weight
        
        if simhash[i] < 0:
            simhash[i] = '0'
        else:
            simhash[i] = '1'
    
    simhash = ''.join(simhash)

    for cururl, curhash in url_index.values():

        similarity = bin(int(simhash, 2)^int(curhash, 2))[2:].zfill(128).count('0')/128.0    

        if (similarity >= 0.92): #THRESHOLD (118+ similar bits out of 128 (10 bit difference))

            return False, None
        
    return True, simhash


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
                    simhash_info = dict()
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

                                #creating features for simhash: getting the token frequency for each document
                                #sinhash_info: dictionary with key as token and value as a 2-list of frequency in document and token's hash value
                                if stem not in simhash_info:
                                    simhash_info[stem] = [1,bin(int(hashlib.md5(stem.encode()).hexdigest(), 16))[2:].zfill(128)] # 128 bit md5 hash
                                else:
                                    simhash_info[stem][0] += 1

                                if stem not in file_index:
                                    file_index[stem] = Posting(docID, stem)
                                
                                file_index[stem].increment_freq()
                                file_index[stem].add_position(wordPosition)
                                
                                wordPosition += 1

                    #sending in the simhash_info to calculate simhash and check for near duplicates
                    #if there exists a near duplicate, we make add_doc to False and we don't add the doc
                    #if there is no near duplicate, we make add_doc to True and return the simhash for the current document to store
                    add_doc, simhash = simhashSimilarity(simhash_info, data['url'])

                    if add_doc:
                        # adding docIDs, frequencies, and URLs to dict and defaultdict
                        for stem, post in file_index.items():
                            if stem not in main_index:
                                main_index[stem] = []
                            post.set_tfWeight(1 + math.log10(post.get_freq()))
                            bisect.insort(main_index[stem], post)
                                    
                        url_index[docID] = (data['url'], simhash)
                            
                        docID += 1
                    
                    if sys.getsizeof(main_index) >= (psutil.virtual_memory()[0] / 2) or psutil.virtual_memory()[2] >= 100:
                        os.chdir("../search-engine-m3")
                        dump()
                        os.chdir("../DEV")

            print(f'Directory {dir} done\n')
            # break

    # ensuring main_index.json gets dumped in inverted-index-m1 directory instead of DEV 
    os.chdir("../search-engine-m3")
    
    if len(main_index) > 0:
        dump()
    
