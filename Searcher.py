import Indexer
from Parser import Parser
from Ranker import Ranker
from gensim.models.doc2vec import Doc2Vec
from sklearn.preprocessing import MinMaxScaler
import pickle
from scipy import spatial
from math import *

class Searcher:
    def __init__(self, corpus_path, results_path, terms_dict, average_doc_length, city_dictionary,
                 doc2vec_model_path, doc2vec_doc_tags_path, stem=False):
        self.corpus_path = corpus_path
        self.results_path = results_path
        self.terms_dict = terms_dict
        self.stem = stem
        self.average_doc_length = average_doc_length
        self.city_dictionary = city_dictionary
        self.ranker = Ranker(corpus_path, results_path, terms_dict, average_doc_length, stem)
        self.doc2vec_model = Doc2Vec.load(doc2vec_model_path)
        file = open(doc2vec_doc_tags_path, 'rb')
        self.doc_tags = pickle.load(file)
        file.close()
        self.stop_words_list = []

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
        else:
            city_docs = None
        doc_list = self.ranker.top_x_bm25_docs_for_query(query, x, b_value, k_value, city_docs_list=city_docs)
        bm25_scores = list(doc_list.values())
        max = bm25_scores[0]
        min = bm25_scores[len(bm25_scores) - 1]
        # scalar = MinMaxScaler()
        # scalar.fit(bm25_scores)
        query_vector = self.doc2vec_model.infer_vector(query)
        # doc2vec_indexes = []
        # for key in doc_list.keys():
        #     doc2vec_indexes.append(self.doc_tags[key])

        max_cosine = None
        min_cosine = None
        similarities = {}
        for doc in doc_list:
            if not self.doc_tags[doc] in self.doc2vec_model.docvecs: # TODO: Need to check why we need this, maybe we to train doc2vec again
                similarities[doc] = 0
            else:
                cosine_sim = abs(1 - spatial.distance.cosine(query_vector,
                                                         self.doc2vec_model.docvecs[self.doc_tags[doc]]))
                if not cosine_sim == float('-inf'):
                    if max_cosine is None or cosine_sim > max_cosine:
                        max_cosine = cosine_sim
                    if min_cosine is None or cosine_sim < min_cosine:
                        min_cosine = cosine_sim
                    similarities[doc] = cosine_sim
                else:
                    similarities[doc] = 0

        final_scores = {}
        for doc in doc_list:
            normalized_cosine_value = (similarities[doc] - min_cosine) / (max_cosine - min_cosine)
            normalized_bm25_value = (doc_list[doc] - min) / (max - min)
            final_scores[doc] = normalized_cosine_value * 0 + normalized_bm25_value * 1

        return final_scores


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

    def search_single_query(self, stop_words_list, posting_directory, query, stem_flag, semantics_flag, city):
        """
        Method searches for only one query. Parses each term and uses Ranker to rank each doc
        Returns top 50 documents for query
        :param stop_words_list: list of stop words
        :param posting_directory: string directory of posting
        :param query: string
        :param stem_flag: True if use stemming, False otherwise.
        :param semantics_flag: True if use semantics, False otherwise.
        :param city: None if search by NO city, list of strings otherwise
        :return: Dictionary of top 50 docs per query
        """
        parser = Parser([stop_words_list])
        query_terms = parser.parser_pipeline([query])



    def search_multiple_queries(self, stop_words_list, posting_directory, queries_text, stem_flag, semantics_flag, city):
        """
        Method searches for each query and returns top 50 documents for each query.
        :param stop_words_list: list of stop words
        :param posting_directory: string directory of posting files
        :param queries_text: text of query file
        :param stem_flag: True if use stemming, False otherwise
        :param semantics_flag: True if use semantics, False otherwise
        :param city: None if no city, List of strings otherwise
        :return: Dictionary of top 50 docs per query
        """
        queries_dict = self.create_queries_from_text(queries_text)
        parser = Parser([stop_words_list])
        for query_num in queries_dict:
            title = queries_dict[query_num][0]
            query_terms = parser.parser_pipeline([title])

    def create_queries_from_text(self, text):
        """
        Method parses tags in text to create and separate queries.
        :param text: text from query file
        :return: Dictionary: Key = query_number, Value = List[title, description, narrative]
        """
        queries = {}
        for i, line in enumerate(text, start=0):
            if line == '<top>':
                start = i
            elif line == '</top>':
                self.analyze_query(queries, text[start + 1:i - 1])

        return queries

    def set_stop_words(self, stop_words):
        """
        Method sets stop words list for Searchers
        :param stop_words: list of strings
        """
        self.stop_words_list = stop_words

    def analyze_query(self, queries, text):
        """
        Method analyzes text and finds query number, title, desc and narrative.
        Adds query to dictionary
        :param queries: dictionary: Key = query_num, Value = [title, desc, narrative]
        :param text: text of query in file
        """
        query_num = ''
        title = ''
        accumulate_desc = False
        accumulate_narr = False
        desc = ''
        narrative = ''
        for line in text:
            if '<num>' in line:
                query_num = line[14:]
            if '<title>' in line:
                title = line[8:]
            if '<desc>' in line:
                accumulate_desc = True
            if '<narr>' in line:
                accumulate_desc = False
                accumulate_narr = True
            if accumulate_desc:
                desc = desc + line
            if accumulate_narr:
                narrative = narrative + line
        queries[query_num] = [title, desc, narrative]
