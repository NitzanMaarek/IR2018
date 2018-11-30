
class Token:
    def __init__(self, token_name):
        self.token_name = token_name
        self.df = 0
        self.doc_dict = {}

    def add_data(self, tuple, doc_num):
        self.df += 1
        self.doc_dict[doc_num] = (tuple[0], tuple[1])

    def string_to_disk(self):
        return ''