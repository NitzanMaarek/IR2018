from gensim.models import Word2Vec
from gensim.models import Doc2Vec
import math
import codecs

class Ranker():
    def __init__(self, corpus_path, results_path, terms_dict, average_doc_length, doc_count, stem=False):
        self.corpus_path = corpus_path
        self.results_path = results_path
        self.terms_dict = terms_dict
        self.doc_count = doc_count
        self.stem = stem
        self.average_doc_length = average_doc_length
        # TODO: make those files
        # self.word2vec_model = Word2Vec.load(results_path + '\\word2vec.model')
        # self.doc2vec_model = Doc2Vec.load(results_path + '\\doc2vec.model')

    def get_term_data_from_posting(self, term, term_dict_value):
        seek_offset = term_dict_value[0]
        if self.stem:
            posting_file_name = 'stp_' + term[:2]
        else:
            posting_file_name = 'tp_' + term[:2]
        with open(self.results_path + '\\terms posting\\' + posting_file_name, 'r', errors='ignore') as file:
            file.seek(int(seek_offset))
            term_posting = file.readline().split()
        return term_posting

    def get_docs_list_from_term_posting(self, terms_posting):
        docs = {}
        for i in range(2, len(terms_posting), 9):
            docs[terms_posting[i]] = i
        return docs

    def get_doc_values_from_terms_posting(self, terms_posting, doc_id):

        for i in range(2, len(terms_posting), 9):
            if terms_posting[i] == doc_id:
                doc_values = []
                for j in range(i, i + 7):
                    doc_values.append(terms_posting[j])
                return doc_values

    def get_term_doc_values(self, term, terms_dict, doc_id):
        terms_posting = self.get_term_data_from_posting(term, terms_dict[term])
        return self.get_doc_values_from_terms_posting(terms_posting, doc_id)

    def get_doc_posting_values(self, posting_file_id, seek_offset):
        if not self.stem:
            posting_file_name = 'doc_posting_' + posting_file_id
        else:
            posting_file_name = 'doc_posting_' + posting_file_id + '_stem'
        with open(self.results_path + '\\\document posting\\' + posting_file_name, 'r', errors='ignore') as file:
            file.seek(int(seek_offset))
            document_posting = file.readline().split()
        return document_posting

    def get_doc_posting_value_by_term_doc_posting_values(self, terms_doc_posting_values):
        return self.get_doc_posting_values(terms_doc_posting_values[5], terms_doc_posting_values[6])


    def bm25_score(self, term, term_idf, doc_id, k_value, b_value, doc_posting):
        # TODO: check term_tf, seems that for every term in the query we will get the same term tf
        # TODO: ADD Entities here

        bm25_terms_values = []
        doc_length = -1

        if term in self.terms_dict:
            if doc_posting is None:
                return 0
            if doc_length == -1:
                doc_posting_values = self.get_doc_posting_value_by_term_doc_posting_values(doc_posting)
                entities_dict = self.get_entities(doc_posting_values)
                if len(doc_posting_values) < 5:
                    print(doc_posting_values)
                doc_posting_len = doc_posting_values[4]
                if doc_posting_len.isnumeric():
                    doc_length = float(doc_posting_len)
            term_tf = float(doc_posting[1])
            numerator = term_tf * (k_value + 1)
            denominator = term_tf + k_value * (1 - b_value + b_value * doc_length / self.average_doc_length)
            bm25_terms_values = term_idf * numerator / denominator

        return bm25_terms_values, entities_dict

    # TODO: TEST THIS FUNCTION
    def top_x_bm25_docs_for_query(self, query, x, b_value, k_value, city_docs_list=None):
        # Need to get the ids and posting values of each top docs
        doc_scores = {}
        doc_term_count = {}
        entities_dict = {}
        for term in query:
            if not term in self.terms_dict:
                if term.lower() in self.terms_dict:
                    term = term.lower()
                else:
                    continue
            term_idf = math.log(self.doc_count / self.terms_dict[term][2], 2)
            terms_posting_data = self.get_term_data_from_posting(term, self.terms_dict[term])
            docs_list = self.get_docs_list_from_term_posting(terms_posting_data)
            for doc, i in docs_list.items():
                doc_term_posting_data = terms_posting_data[i:i + 7]
                # If we were given a specific city we will check if the doc has the given city attribute
                if not city_docs_list is None:
                    if not doc in city_docs_list:
                        continue
                doc_bm25_score, doc_entities_dict = self.bm25_score(term, term_idf, doc, k_value, b_value, doc_term_posting_data)

                # Giving bonus for documents with terms in the title
                # if doc_term_posting_data[4] == 'True': # TODO: check if this is the right place and if this is the right value
                #     doc_bm25_score += 2 * doc_bm25_score

                if doc in doc_scores.keys():
                    doc_scores[doc] = doc_scores[doc] + doc_bm25_score
                else:
                    doc_scores[doc] = doc_bm25_score
                    if not doc_entities_dict is None:
                        entities_dict[doc] = doc_entities_dict

                if doc in doc_term_count.keys():
                    doc_term_count[doc] += 1
                else:
                    doc_term_count[doc] = 1
            print('finished ' + term)
        # doc_sorted_scores = sorted(doc_scores.keys(), reverse=True)

        term_count = len(query)
        for doc in doc_scores:
            # if doc_term_count[doc] == term_count:
            doc_scores[doc] = doc_scores[doc] + doc_scores[doc] * (doc_term_count[doc] - 1) * (len(query) - 1)

        docs_sorted_by_score = sorted(doc_scores.items(), key=lambda kv: kv[1], reverse=True)
        ids_with_scores = {}
        min_bound = min(len(docs_sorted_by_score), x)

        top_docs_entities_dict = {}
        for i in range(0, min_bound):
            ids_with_scores[docs_sorted_by_score[i][0]] = docs_sorted_by_score[i][1]
            if docs_sorted_by_score[i][0] in entities_dict:
                top_docs_entities_dict[docs_sorted_by_score[i][0]] = entities_dict[docs_sorted_by_score[i][0]]
            else:
                top_docs_entities_dict[docs_sorted_by_score[i][0]] = None

        return ids_with_scores, top_docs_entities_dict

    def get_entities(self, doc_posting):
        if '<' in doc_posting:
            index = doc_posting.index('<')
            entities_data = doc_posting[index + 1 : len(doc_posting) - 1]
            entities_dict = {}
            for i in range(0, len(entities_data), 2):
                entities_dict[entities_data[i]] = entities_data[i + 1]
            return entities_dict
        else:
            return None
