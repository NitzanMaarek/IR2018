from gensim.models import Word2Vec
from gensim.models import Doc2Vec


class Ranker():
    def __init__(self, corpus_path, results_path, terms_dict, average_doc_length, stem=False):
        self.corpus_path = corpus_path
        self.results_path = results_path
        self.terms_dict = terms_dict
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
        with open(self.results_path + '\\terms posting\\' + posting_file_name) as file:
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
        with open(self.results_path + '\\\document posting\\' + posting_file_name) as file:
            file.seek(int(seek_offset))
            document_posting = file.readline().split()
        return document_posting

    def get_doc_posting_value_by_term_doc_posting_values(self, terms_doc_posting_values):
        return self.get_doc_posting_values(terms_doc_posting_values[5], terms_doc_posting_values[6])


    def bm25_score(self, query, doc_id, k_value, b_value, average_doc_length, terms_dict):
        # I assume query is list of string after parsing
        bm25_terms_values = []
        doc_length = -1
        for term in query:
            term = term.lower()
            if term in terms_dict:
                term_doc_values = self.get_term_doc_values(term, terms_dict, doc_id)
                if term_doc_values is None:
                    continue
                if doc_length == -1:
                    doc_posting_values = self.get_doc_posting_value_by_term_doc_posting_values(term_doc_values)
                    doc_posting_len = doc_posting_values[4]
                    if doc_posting_len.isnumeric():
                        doc_length = float(doc_posting_len)
                term_tf = float(term_doc_values[1])
                numerator = term_tf * (k_value + 1)
                denominator = term_tf + k_value * (1 - b_value + b_value * doc_length / average_doc_length)
                bm25_terms_values.append(numerator / denominator)

        return sum(bm25_terms_values)

    # TODO: TEST THIS FUNCTION
    def top_x_bm25_docs_for_query(self, query, x, b_value, k_value, average_doc_length, terms_dict):
        # Need to get the ids and posting values of each top docs
        doc_scores = {}
        for term in query:
            terms_posting_data = self.get_term_data_from_posting(term, terms_dict)
            docs_list = self.get_docs_list_from_term_posting(terms_posting_data)
            for doc, i in docs_list.items():
                if not doc in doc_scores:
                    doc_term_posting_data = terms_posting_data[i:i + 6]
                    doc_id = doc_term_posting_data[0]
                    doc_bm25_score = self.bm25_score(query, doc_id, k_value, b_value, average_doc_length, terms_dict)
                    if doc_bm25_score in doc_scores:
                        doc_scores[doc_bm25_score].append(doc_id)
                    else:
                        doc_scores[doc_bm25_score] = [doc_id]

        doc_sorted_scores = sorted(doc_scores.keys(), reverse=True)

        ids_with_scores = {}
        counter = 0
        for i in range(0, x):
            score = doc_sorted_scores[i]
            docs_ids = doc_scores[score]
            if counter + len(docs_ids) < x:
                for doc in docs_ids:
                    ids_with_scores[doc] = score
                counter += len(docs_ids)
            elif counter < x:
                i = 0
                while counter < x:
                    ids_with_scores[docs_ids[i]] = score
                    counter += 1

        return ids_with_scores