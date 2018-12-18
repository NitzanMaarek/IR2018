import Indexer
from Ranker import Ranker

class Searcher:
    def __init__(self, corpus_path, results_path, terms_dict, average_doc_length, stem=False):
        self.corpus_path = corpus_path
        self.results_path = results_path
        self.terms_dict = terms_dict
        self.stem = stem
        self.average_doc_length = average_doc_length
        self.ranker = Ranker(corpus_path, results_path, terms_dict, average_doc_length, stem)

    def update_parameters(self, corpus_path=None, results_path=None, terms_dict=None,
                          average_doc_length=None, stem=None):
        if not corpus_path is None:
            self.corpus_path = corpus_path
        if not results_path is None:
            self.results_path = results_path
        if not terms_dict is None:
            self.terms_dict = terms_dict
        if not stem is None:
            self.stem = stem
        if not average_doc_length is None:
            self.average_doc_length = average_doc_length


    def search(self, query, x=1000, b_value=0.5, k_value=1.5):
        doc_list = Ranker.top_x_bm25_docs_for_query(query, x, b_value, k_value)
        # TODO: add ranking with doc2vec and combine it with the bm25 rank
