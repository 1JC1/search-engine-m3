import json
class Posting:
    '''class object for keeping track of instances in the index'''
    def __init__(self, inputDocID = None, inputToken = None, inputFreq = 0, inputList = []) -> None:
        self.docID = inputDocID
        self.token = inputToken
        self.freq = inputFreq
        self.positionList = inputList
        
    def get_docID(self):
        return self.docID
    
    def get_freq(self):
        return self.freq
    
    def get_positionList(self):
        return self.positionList
    
    def get_token(self):
        return self.token
        
    def set_docID(self, newDocID):
        self.docID = newDocID
        
    def set_token(self, newToken):
        self.token = newToken
        
    def increment_freq(self):
        self.freq += 1
        
    def add_position(self, index):
        self.positionList.append(index)
        
    def __lt__(self, other):
        return self.docID < other.docID
    
    def __eq__(self, other):
        return self.docID == other.docID and self.token == other.token

    def __hash__(self):
        return hash((self.docID, self.token))

    def __str__(self) -> str:
        return f"Posting(inputDocID={self.docID}, inputToken={self.token}, inputFreq={self.freq}, inputList={self.positionList})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    # allows use of json.dump into main_index.json
    def to_json(self):
        # return json.dumps(dict(self), ensure_ascii=False)
        return json.dumps(self, default=lambda o: o.__dict__)