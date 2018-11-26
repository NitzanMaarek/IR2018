import nltk

class Indexer():
    def __init__(self, posting_path, q):
        self.dict = {}
        self.posting_path = posting_path
        self.q = q

    def run_listener(self):
        '''listens for messages on the q, writes to file. '''
        with open('listener output.txt', 'a+') as file:
            while 1:
                doc = self.q.get()
                if str(doc) == 'kill':
                    print('killed')
                    break
                # file.write("Indexer received doc: " + str(doc.doc_num) + '\n')
                # TODO: call function that uses data here