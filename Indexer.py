import multiprocessing as mp

# class Indexer():
#     def __init__(self, posting_path):
#         self.dict = {}
#         self.posting_path = posting_path
        # self.files_per_iter = files_per_iter

def merge_docs(doc_list):
    with open('indexer output.txt', 'a+') as file:
        file.write("docs num: " + str(len(doc_list)) + "\n")
