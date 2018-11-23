import nltk

class Indexer():
    def __init__(self, posting_path, q):
        self.dict = {}
        self.posting_path = posting_path
        self.lister()

    def listener(q):
        '''listens for messages on the q, writes to file. '''
        while 1:
            document = q.get()
            if str(document) == 'kill':
                print
                'killed'
                break
            # TODO: call function that uses data here