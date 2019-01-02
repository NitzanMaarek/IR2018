import Indexer
from Parser import Parser
from Ranker import Ranker
from gensim.models.doc2vec import Doc2Vec
from gensim.models import KeyedVectors
import pickle
import operator
import os
from scipy import spatial

class Searcher:
    def __init__(self, corpus_path, results_path,
                 doc2vec_model_path='doc2vec.model', doc2vec_doc_tags_path='doc2vec_doc tags', semantic_flag=False, stem=False):
        """
        Searcher object that is in charge of using the posting and dictionaries to search the corpus
        :param corpus_path: path to where the corpus is stored # TODO: check if we need this
        :param results_path: path to where all the results file are stored
        :param doc2vec_model_path: doc2vec model file name
        :param doc2vec_doc_tags_path: doc2vec tags dictionary file name
        :param semantic_flag: use semantics or not
        :param stem: search on stem results or nor
        """
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

        self.stem_doc2vec_model = Doc2Vec.load(results_path + '\\stem_' + doc2vec_model_path)
        with open(results_path + '\\stem_' + doc2vec_doc_tags_path, 'rb') as file:
            self.stem_doc_tags = pickle.load(file)

        self._get_average_doc_length()
        # self.word2vec_model = KeyedVectors.load_word2vec_format('word2vec.model', binary=True)
        self.word2vec_model = KeyedVectors.load(results_path + '\\' + 'word2vec.model')
        self.ranker = Ranker(corpus_path, results_path, self.terms_dict, self.average_doc_length, self.doc_count, stem)

    def update_parameters(self, corpus_path=None, results_path=None, terms_dict=None,
                          average_doc_length=None, semantic_flag=None, stem=None):
        """
        Method which is used to change all or some of the searcher parameters
        :param corpus_path: path to where the corpus is stored
        :param results_path: path to where all the results file are stored
        :param terms_dict: update the terms dictionary
        :param average_doc_length: update the average document length
        :param semantic_flag: use semantics or not
        :param stem: update value of search on stem results or nor
        """
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
            if 'stem' not in file:
                with open(dir_path + '\\' + file) as f:
                    lines = f.readlines()
                    for line in lines:
                        docs_len.append(int(line.split()[2]))
        self.average_doc_length = sum(docs_len) / len(docs_len)
        self.doc_count = len(docs_len)

    def search(self, query, query_description=None, x=50, b_value=0.5, k_value=1.5, city=None):

        if not city is None:
            city_docs = self.get_city_docs(city)
        else:
            city_docs = None
        doc_list, entities_dict = self.ranker.top_x_bm25_docs_for_query(
            query + query_description, x * 4, b_value, k_value, city_docs_list=city_docs)
        bm25_scores = list(doc_list.values())
        max = bm25_scores[0]
        min = bm25_scores[len(bm25_scores) - 1]

        query_vector = self.doc2vec_model.infer_vector(query)

        if not query_description is None:
            description_vector = self.doc2vec_model.infer_vector(query_description)

        query_max_cosine = None
        query_min_cosine = None

        desc_max_cosine = None
        desc_min_cosine = None
        similarities = {}
        description_similarities = {}

        for doc in doc_list:
            best_cosine_value = self.get_best_paragraph_cosine(query_vector, doc)

            if best_cosine_value == float('-inf'):
                similarities[doc] = 0
            else:
                similarities[doc] = best_cosine_value

            # if best_cosine_value > 0 and not best_cosine_value == float('-inf'):
            #     if query_max_cosine is None or best_cosine_value > query_max_cosine:
            #         query_max_cosine = best_cosine_value
            #     if query_min_cosine is None or best_cosine_value < query_min_cosine:
            #         query_min_cosine = best_cosine_value
            #     similarities[doc] = best_cosine_value
            # else:
            #     similarities[doc] = 0

            if not query_description is None:
                best_cosine_value = self.get_best_paragraph_cosine(description_vector, doc)

                if best_cosine_value == float('-inf'):
                    description_similarities[doc] = 0
                else:
                    description_similarities[doc] = best_cosine_value

                # if not best_cosine_value == float('-inf'):
                #     if desc_max_cosine is None or best_cosine_value > desc_max_cosine:
                #         desc_max_cosine = best_cosine_value
                #     if desc_min_cosine is None or best_cosine_value < desc_min_cosine:
                #         desc_min_cosine = best_cosine_value
                #     description_similarities[doc] = best_cosine_value
                # else:
                #     description_similarities[doc] = 0

        final_scores = {}
        for doc in doc_list:
            normalized_bm25_value = (doc_list[doc] - min) / (max - min)
            # normalized_cosine_value = (similarities[doc] - query_min_cosine) / (query_max_cosine - query_min_cosine)

            if not query_description is None:
                # desc_norm_cosine = (similarities[doc] - desc_min_cosine) / (desc_max_cosine - desc_min_cosine)
                score = similarities[doc] * 0.1 + normalized_bm25_value * 0.8 + description_similarities[doc] * 0.1
            else:
                score = similarities[doc] * 0.2 + normalized_bm25_value * 0.8

            final_scores[doc] = score

        sorted_query_results = sorted(final_scores.items(), key=operator.itemgetter(1), reverse=True)

        results_dict = {}
        # Inserting the values in entities dict to a new dictionary to get a sorted dictionary
        counter = 0
        for doc_data in sorted_query_results:
            doc_id = doc_data[0]
            results_dict[doc_id] = entities_dict[doc_id]
            counter += 1
            if counter == x:
                break

        return results_dict


    # TODO: check everything below
    def get_city_docs(self, city_list):
        # Change to dictionary
        all_city_docs = []
        for city in city_list:
            city = city.upper()
            city_posting = self._get_city_data_from_posting(city)
            city_docs = list(self._get_docs_dict_from_term_posting(city_posting).keys())
            all_city_docs = all_city_docs + city_docs
        return all_city_docs

    def _get_docs_dict_from_term_posting(self, city_posting):
        docs = {}
        first_index = city_posting.index('<') + 1
        for i in range(first_index, len(city_posting), 5):
            docs[city_posting[i]] = i
        return docs

    def _get_city_data_from_posting(self, city):
        seek_offset = self.city_dictionary[city][0]
        if self.stem:
            cities_posting_path = '\\cities\\cities posting stem'
        else:
            cities_posting_path = '\\cities\\cities posting'

        with open(self.results_path + cities_posting_path) as file:
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
        results = {}
        semantic_result = {}
        parser = Parser(stop_words_list)
        query_terms_dictionary = parser.parser_pipeline([query], stem_flag)
        query_terms_list = parser.get_tokens_after_parse()
        self.update_parameters(results_path=results_path, stem=stem_flag, semantic_flag=semantic_flag)
        search_result = self.search(query_terms_list, city=city)
        if semantic_flag:
            semantic_query = self.get_semantic_altered_query(query_terms_list)
            semantic_search_results = self.search(semantic_query, city=city)
            semantic_result = {'1': semantic_search_results}
        result = {'1': search_result}

        return result, semantic_result

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
        semantic_results = {}
        for query_num in queries_dict:
            title = queries_dict[query_num][0]
            query_terms = parser.parser_pipeline([title], False)
            query_terms_list = parser.get_tokens_after_parse()
            parser.erase_dictionary()

            desc = queries_dict[query_num][1]
            parser.parser_pipeline([desc], False)
            desc_terms_list = parser.get_tokens_after_parse()

            # Running query with semantics
            if semantic_flag:
                semantic_query = self.get_semantic_altered_query(query_terms_list)
                semantic_desc = self.get_semantic_altered_query(desc_terms_list)
                parser.erase_dictionary()

                if stem_flag:
                    parser.parser_pipeline(semantic_query, stem=stem_flag)
                    semantic_query = parser.get_tokens_after_parse()
                    parser.erase_dictionary()
                    parser.parser_pipeline([semantic_desc], stem_flag)
                    semantic_desc = parser.get_tokens_after_parse()
                    parser.erase_dictionary()

                semantic_search_results = self.search(semantic_query,
                                                      query_description=semantic_desc, city=city)
                semantic_results[query_num] = semantic_search_results

            # Applying stem for normal query
            if stem_flag:
                parser.parser_pipeline(query_terms_list, stem_flag)
                query_terms_list = parser.get_tokens_after_parse()
                parser.erase_dictionary()
                parser.parser_pipeline([desc], stem_flag)
                desc_terms_list = parser.get_tokens_after_parse()

            curr_result = self.search(query_terms_list, query_description=desc_terms_list, city=city)

            results[query_num] = curr_result

        return results, semantic_results

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
                continue
            if '<narr>' in line:
                accumulate_desc = False
                accumulate_narr = True
                continue
            if accumulate_desc:
                desc = desc + line
            if accumulate_narr:
                narrative = narrative + line
        queries[query_num] = [title, desc, narrative]


    def get_most_similar_word(self, original_word, similarity_threshold=0.6):
        """
        Return the most similar word to a given word using the word2vec model
        The returned word won't contain the given word and the cosine similarity between them must
        be greater then the given threshold. The similar word must stand to those constraints
        so it will have a similar meaning and not be another form of the given word.
        If the given word is not in our model (which means it is not in out corpus we return None)
        :param original_word: The word that we want to get an other word which is similar to it
        :param similarity_threshold: cosine similarity threshold
        :return: Similar but different word
        """
        original_word = original_word.lower()
        if original_word in self.word2vec_model.wv:
            similar_words = self.word2vec_model.wv.most_similar(original_word)
            for similar_word_tuple in similar_words:
                similar_word = similar_word_tuple[0]

                if similar_word.lower() in self.terms_dict:
                    similar_word = similar_word.lower()
                elif similar_word.upper() in self.terms_dict:
                    similar_word = similar_word.upper()

                if similar_word in self.terms_dict:
                    # similarity = self.word2vec_model.wv.similarity(original_word, similar_word)
                    if similar_word_tuple[1] > similarity_threshold and original_word not in similar_word:
                        return similar_word
        else:
            return None

    def get_semantic_altered_query(self, query):
        new_query = []
        for term in query:
            new_term = self.get_most_similar_word(term)
            if new_term is not None:
                new_query.append(new_term)
            # else:
            #     new_query.append(term)
        return query + new_query

    def get_best_paragraph_cosine(self, query_vector, doc_id):
        counter = 0
        max_cosine = 0
        next_paragraph = doc_id + ' ' + str(counter)
        while next_paragraph in self.doc_tags.keys():

            if self.stem:
                tag = self.stem_doc_tags[next_paragraph]
                paragraph_vector = self.stem_doc2vec_model.docvecs[tag]
            else:
                tag = self.doc_tags[next_paragraph]
                paragraph_vector = self.doc2vec_model.docvecs[tag]

            # cosine_sim = abs(1 - spatial.distance.cosine(query_vector, paragraph_vector))
            cosine_sim = 1 - spatial.distance.cosine(query_vector, paragraph_vector)
            if cosine_sim > max_cosine:
                max_cosine = cosine_sim

            counter += 1
            next_paragraph = doc_id + ' ' + str(counter)

        title = doc_id + ' title'
        if title in self.doc_tags.keys():

            if self.stem:
                tag = self.stem_doc_tags[title]
                title_vector = self.stem_doc2vec_model.docvecs[tag]
            else:
                tag = self.doc_tags[title]
                title_vector = self.doc2vec_model.docvecs[tag]

            # cosine_sim = abs(1 - spatial.distance.cosine(query_vector, title_vector))
            cosine_sim = 1 - spatial.distance.cosine(query_vector, title_vector)
            if cosine_sim > max_cosine:
                max_cosine = cosine_sim

        return max_cosine