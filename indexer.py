import json, os, re, sys, bisect, psutil, math
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from Posting import Posting
from collections import defaultdict
from string import ascii_lowercase
from timeit import default_timer as timer
import hashlib

#GLOBALS
letter_list = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z', 'num']
main_index = dict()
disk_index = dict() #has the open files to each of the letter.txt's
index_of_index = dict() #stores all the words and its position in the disk_index
url_index = dict()
anchor_dict = defaultdict(int)
stemmer = SnowballStemmer("english", ignore_stopwords=True)
newpath = "file_index"
docID = 0


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
        tokenize(title, token_nested_dict, 18)
    #h1, h2/h3, h4/h5/h6
    for num in range(0, 6):
        for head in soup.findAll('h' + str(num)):
            tokenize(head, token_nested_dict, 13 - num)
    #strong
    for strong in soup.findAll('strong'):
        tokenize(strong, token_nested_dict, 8)
    #bold
    for bolded in soup.findAll('bold'):
        tokenize(bolded, token_nested_dict, 5)
    #emphasized
    for em in soup.findAll('em'):
        tokenize(em, token_nested_dict, 3)
    #italics
    for italics in soup.findAll('i'):
        tokenize(italics, token_nested_dict, 1)
    #anchor tags
    for anchor in soup.findAll('a', href=True):
        anchor_dict[anchor.get('href').split('#', maxsplit=1)[0]] += 1


def close_files():
    for f in disk_index.values():
        f.close()


def open_files():
    os.chdir(newpath)
    for char in letter_list:
        f = open(f"{char}.txt", "r") #r for reading only, wont have to write since this only gets called for 
        disk_index[char] = f
    os.chdir("../")


def load_json():

    os.chdir(newpath)
    with open("anchor_index.json", "r") as f:
        global anchor_dict
        anchor_dict = json.load(f)

    with open("url_index.json", "r") as f:
        global url_index
        url_index = json.load(f)

    #converting docIDs to integers as they end up as strings when loading it from file
    url_index = {int(id):v for id, v in url_index.items()}
    
    os.chdir("../")
    return url_index, anchor_dict


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
            p += 1

        elif main_tokens[p] > disk_token:
            merged_file.write(f"{disk_token}|{disk_postings}\n")
            line = disk_file.readline()
            if line:
                disk_line_info = line.strip().split("|")
                disk_token = disk_line_info[0]
                disk_postings = eval(disk_line_info[1])

        else:
            postings = union_postings(main_index[main_tokens[p]], disk_postings)
            merged_file.write(f"{disk_token}|{postings}\n")
            p += 1
            line = disk_file.readline()
            if line:
                disk_line_info = line.strip().split("|")
                disk_token = disk_line_info[0]
                disk_postings = eval(disk_line_info[1])

    if p < len(main_tokens):
        for tok in main_tokens[p:]:
            merged_file.write(f"{tok}|{main_index[tok]}\n")

    elif line:
        while line:
            merged_file.write(f"{disk_token}|{disk_postings}\n")
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
        disk_index[curr].close()

        os.remove(f"{curr}.txt")
        os.rename(f"new_{curr}.txt", f"{curr}.txt")
        
        disk_index[curr] = open(f"{curr}.txt", "r")

    
    main_index.clear()
    os.chdir("../")


def simhashSimilarity(simhash_info: dict[str: list[int, str]]) -> tuple[int, str or None]:

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

    for _1, curhash, _2 in url_index.values():

        similarity = bin(int(simhash, 2)^int(curhash, 2))[2:].zfill(128).count('0')/128.0    

        if (similarity >= 0.92): #THRESHOLD (118+ similar bits out of 128 (10 bit difference))

            return False, None
        
    return True, simhash


def indexer():
    '''Read through JSON file, create docID, parse content with listed encoding, tokenize,
        stemming and other language processing, add doc as postings to inverted index (dictionary) '''
    global main_index
    global url_index
    global docID
    dirNum = 1

    # changing into the DEV directory and opening it
    os.chdir("../DEV")
    
    print("Indexing started...\n")
    index_start = timer()
    
    for dir in os.listdir():
        if dir != '.DS_Store':
            print("*************************************************")
            print(f"Directory {dir} started\n")
            dir_start = timer()
            
            # opening the subdirectories in dev directory
            for file in os.listdir(dir):
                
                # opening each file in subdirectories and parsing data
                if os.path.splitext(file)[1] == '.json':
                    file_index = dict()
                    simhash_info = dict()
                    tag_dict = defaultdict(int)
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
                        tags(soup, tag_dict)
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
                    add_doc, simhash = simhashSimilarity(simhash_info)

                    if add_doc:
                        weight_sum = 0
                        
                        # adding docIDs, frequencies, and URLs to dict and defaultdict
                        for stem, post in file_index.items():
                            if stem not in main_index:
                                main_index[stem] = []
                            # html_score = 0 if stem not in tag_dict else math.log10(tag_dict[stem])
                            weight = 1 + math.log10(post.get_freq() + tag_dict[stem])
                            post.set_tfWeight(weight)
                            weight_sum += (weight ** 2)
                            bisect.insort(main_index[stem], post)
                                    
                        url_index[docID] = (data['url'].split('#', maxsplit=1)[0], simhash, math.sqrt(weight_sum))
                            
                        docID += 1
                        
            dir_end = timer()
            print(f"Time to create main index: {dir_end - dir_start} sec")
            print(f"Size of Main Index: {sys.getsizeof(main_index)} bytes\n")

            os.chdir("../search-engine-m3")
            print("Dumping...")
            dump_start = timer()
            dump()
            dump_end = timer()
            print(f"Time to dump: {dump_end - dump_start} sec\n")
            os.chdir("../DEV")

            print(f'Directory {dir} done')
            print("*************************************************\n")
            
            dirNum += 1

    index_end = timer()
    print("Indexing Completed")
    print("--------------------------------------------------")
    print(f"Total time to index: {(index_end - index_start)/60} min")
    print(f"Total Directories indexed: {dirNum}")
    print(f"Total files indexed: {docID + 1}\n")

    # ensuring main_index.json gets dumped in inverted-index-m1 directory instead of DEV 
    os.chdir("../search-engine-m3")
    
    url_set = set()

    for cur_url, _1, _2 in url_index.values():
        url_set.add(cur_url)

    #removing anchor urls that is not in our url_set of given files
    anchor_index = dict()
    for anchor_url, count in anchor_dict.items():
        if anchor_url in url_set:
            anchor_index[anchor_url] = count

    os.chdir(newpath)

    print("Dumping json...")
    
    with open("url_index.json", 'w') as f:
        json.dump(url_index, f)
        print("URL index made")
    
    with open("anchor_index.json", 'w') as f:
        json.dump(anchor_index, f)
        print("Anchor index made")
    
    os.chdir("../")

    return url_index, anchor_dict

