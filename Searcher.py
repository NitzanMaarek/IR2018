import Indexer
from Ranker import Ranker

class Searcher:
    def __init__(self, corpus_path, results_path, terms_dict, average_doc_length, city_dictionary, stem=False):
        self.corpus_path = corpus_path
        self.results_path = results_path
        self.terms_dict = terms_dict
        self.stem = stem
        self.average_doc_length = average_doc_length
        self.city_dictionary = city_dictionary
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


    def search(self, query, x=1000, b_value=0.5, k_value=1.5, city=None):
        if not city is None:
            city_docs = self.get_city_docs(city.upper()) # Work in progress

        doc_list = self.ranker.top_x_bm25_docs_for_query(query, x, b_value, k_value, city_docs_list=city_docs)
        return doc_list
        # TODO: add ranking with doc2vec and combine it with the bm25 rank


    # TODO: check everything below
    def get_city_docs(self, city):
        # Change to dictionary
        city_posting = self._get_city_data_from_posting(city)
        return self._get_docs_list_from_term_posting(city_posting)

    def _get_docs_list_from_term_posting(self, city_posting):
        docs = {}
        first_index = city_posting.index('<') + 1
        for i in range(first_index, len(city_posting), 5):
            docs[city_posting[i]] = i
        return docs

    def _get_city_data_from_posting(self, city):
        seek_offset = self.city_dictionary[city][0]
        with open(self.results_path + '\\cities\\cities posting') as file:
            file.seek(int(seek_offset))
            city_posting = file.readline().split()
        return city_posting