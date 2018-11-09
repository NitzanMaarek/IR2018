import nltk

class Indexer():
    def __init__(self, posting_path):
        self.dict = {}
        self.posting_path = posting_path

    # def index_files(self, ):