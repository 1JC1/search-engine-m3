class Posting:
    '''class object for keeping track of instances in the index'''
    def __init__(self, inputDocID = None, inputToken = None, inputFreq = 0, inputWeight = None, inputList = []) -> None:
        self.docID = inputDocID
        self.token = inputToken
        self.freq = inputFreq
        self.tfWeight = inputWeight
        self.positionList = inputList
        
    def get_docID(self):
        return self.docID
    
    def get_freq(self):
        return self.freq
    
    def get_token(self):
        return self.token
    
    def get_tfWeight(self):
        return self.tfWeight
    
    def get_positionList(self):
        return self.positionList
        
    def set_docID(self, newDocID):
        self.docID = newDocID
        
    def set_token(self, newToken):
        self.token = newToken
        
    def set_tfWeight(self, newWeight):
        self.tfWeight = newWeight
        
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
        return f"Posting(inputDocID={self.docID}, inputToken={self.token}, inputFreq={self.freq}, inputWeight = {self.tfWeight}, inputList={self.positionList})"
    
    def __repr__(self) -> str:
        return self.__str__()