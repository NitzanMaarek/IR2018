import Indexer
from Parser import Parser
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
