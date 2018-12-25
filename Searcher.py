import Indexer
from Parser import Parser
from Ranker import Ranker
from gensim.models.doc2vec import Doc2Vec
import pickle
import operator
import os
from scipy import spatial

class Searcher:
    def __init__(self, corpus_path, results_path,
                 doc2vec_model_path='doc2vec.model', doc2vec_doc_tags_path='doc tags', semantic_flag=False, stem=False):
        self.corpus_path = corpus_path
        self.results_path = results_path
        if stem:
            self.terms_dict = Indexer.load_obj(self.results_path, 'stem main terms dictionary', directory= '')
        else:
            self.terms_dict = Indexer.load_obj(self.results_path, 'main terms dictionary', directory= '')
        self.stem = stem
        self.semantic_flag = semantic_flag
        self.city_dictionary = Indexer.load_obj(self.results_path, 'cities dictionary', directory='cities')
        self.doc2vec_model = Doc2Vec.load(results_path + '\\' + doc2vec_model_path)
        with open(results_path + '\\' + doc2vec_doc_tags_path, 'rb') as file:
            self.doc_tags = pickle.load(file)
        self._get_average_doc_length()
        self.ranker = Ranker(corpus_path, results_path, self.terms_dict, self.average_doc_length, self.doc_count, stem)

    def update_parameters(self, corpus_path=None, results_path=None, terms_dict=None,
                          average_doc_length=None, semantic_flag=None, stem=None):
        if not corpus_path is None:
            self.corpus_path = corpus_path
        if not results_path is None:
            self.results_path = results_path
        if not terms_dict is None:
            self.terms_dict = terms_dict
        if not stem is None:
            self.stem = stem
        if not semantic_flag is None:
            self.semantic_flag = semantic_flag
        if not average_doc_length is None:
            self.average_doc_length = average_doc_length

    def _get_average_doc_length(self):
        docs_len = []
        dir_path = self.results_path + '\\document posting'
        for file in os.listdir(dir_path):
            with open(dir_path + '\\' + file) as f:
                lines = f.readlines()
                for line in lines:
                    docs_len.append(int(line.split()[2]))
        self.average_doc_length = sum(docs_len) / len(docs_len)
        self.doc_count = len(docs_len)

    def search(self, query, relevant=None, not_relevant=None, x=50, b_value=0.5, k_value=1.5, city=None):
        if not city is None:
            city_docs = self.get_city_docs(city.upper())  # Work in progress
        else:
            city_docs = None
        doc_list = self.ranker.top_x_bm25_docs_for_query(query, x, b_value, k_value, city_docs_list=city_docs)
        bm25_scores = list(doc_list.values())
        max = bm25_scores[0]
        min = bm25_scores[len(bm25_scores) - 1]

        if not relevant is None:
            relevant_vector = self.doc2vec_model.infer_vector(relevant)
        if not not_relevant is None:
            not_relevant_vector = self.doc2vec_model.infer_vector(not_relevant)

        max_cosine = None
        min_cosine = None
        max_cosine_not = None
        min_cosine_not = None
        similarities = {}
        similarities_not = {}
        for doc in doc_list:
            if not self.doc_tags[doc] in self.doc2vec_model.docvecs: # TODO: Need to check why we need this, maybe we to train doc2vec again
                similarities[doc] = 0
            else:
                if not relevant is None or not not_relevant is None:
                    doc_title = doc + ' title'
                    if doc_title in self.doc_tags:
                        doc_vector = (self.doc2vec_model.docvecs[self.doc_tags[doc]] \
                                      + self.doc2vec_model.docvecs[self.doc_tags[doc_title]]) / 2
                    else:
                        doc_vector = + self.doc2vec_model.docvecs[self.doc_tags[doc]]

                    if not relevant is None:
                        cosine_sim = abs(1 - spatial.distance.cosine(relevant_vector, doc_vector))
                        if not cosine_sim == float('-inf'):
                            if max_cosine is None or cosine_sim > max_cosine:
                                max_cosine = cosine_sim
                            if min_cosine is None or cosine_sim < min_cosine:
                                min_cosine = cosine_sim
                            similarities[doc] = cosine_sim
                        else:
                            similarities[doc] = 0

                    if not not_relevant is None:
                        cosine_sim_not = abs(1 - spatial.distance.cosine(not_relevant_vector, doc_vector))
                        if not cosine_sim_not == float('-inf'):
                            if max_cosine_not is None or cosine_sim_not > max_cosine_not:
                                max_cosine_not = cosine_sim_not
                            if min_cosine_not is None or cosine_sim_not < min_cosine_not:
                                min_cosine_not = cosine_sim_not
                            similarities_not[doc] = cosine_sim_not
                        else:
                            similarities[doc] = 0

        final_scores = {}
        for doc in doc_list:
            if not relevant is None:
                normalized_cosine_value = (similarities[doc] - min_cosine) / (max_cosine - min_cosine)
            else:
                normalized_cosine_value = 0

            if not not_relevant is None:
                normalized_cosine_not_value = (similarities_not[doc] - min_cosine_not) / (max_cosine_not - min_cosine_not)
            else:
                normalized_cosine_not_value = 0

            normalized_bm25_value = (doc_list[doc] - min) / (max - min)
            final_scores[doc] = normalized_cosine_value * 0 + \
                                normalized_bm25_value * 1 - normalized_cosine_not_value * 0

        sorted_query_results = sorted(final_scores.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_query_results


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

    def search_single_query(self, stop_words_list, results_path, query, stem_flag, semantic_flag, city=None):
        """
        Method searches for only one query. Parses each term and uses Ranker to rank each doc
        Returns top 50 documents for query
        :param stop_words_list: list of stop words
        :param results_path: string directory of posting
        :param query: string
        :param stem_flag: True if use stemming, False otherwise.
        :param semantic_flag: True if use semantics, False otherwise.
        :param city: None if search by NO city, list of strings otherwise
        :return: Dictionary of top 50 docs per query
        """
        parser = Parser(stop_words_list)
        query_terms_dictionary = parser.parser_pipeline([query], stem_flag)
        query_terms_list = parser.get_tokens_after_parse()
        self.update_parameters(results_path=results_path, stem=stem_flag, semantic_flag=semantic_flag)
        search_result = self.search(query_terms_list, city=city)
        result = {'1': search_result}
        return result


    def search_multiple_queries(self, stop_words_list, results_path, queries_text, stem_flag, semantic_flag, city=None):
        """
        Method searches for each query and returns top 50 documents for each query.
        :param stop_words_list: list of stop words
        :param results_path: string directory of posting files
        :param queries_text: text of query file
        :param stem_flag: True if use stemming, False otherwise
        :param semantic_flag: True if use semantics, False otherwise
        :param city: None if no city, List of strings otherwise
        :return: Dictionary of top 50 docs per query
        """
        self.update_parameters(results_path=results_path, stem=stem_flag, semantic_flag=semantic_flag)
        queries_dict = self.create_queries_from_text(queries_text)
        parser = Parser(stop_words_list)
        results = {}
        for query_num in queries_dict:
            title = queries_dict[query_num][0]
            query_terms = parser.parser_pipeline([title], stem_flag)
            query_terms_list = parser.get_tokens_after_parse()
            curr_result = self.search(query_terms_list, city=city)
            results[query_num] = curr_result
        return results

    def create_queries_from_text(self, text):
        """
        Method parses tags in text to create and separate queries.
        :param text: text from query file
        :return: Dictionary: Key = query_number, Value = List[title, description, narrative]
        """
        queries = {}
        for i, line in enumerate(text, start=0):
            line = line.replace('\n', '')
            if '<top>' in line:
                start = i
            elif '</top>' in line:
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
        # TODO: check this works fine
        query_num = ''
        title = ''
        accumulate_desc = False
        accumulate_narr = False
        desc = ''
        narrative = ''
        for line in text:
            line = line.replace('\n', '')
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
