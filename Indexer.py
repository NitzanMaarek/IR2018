# import h5py
import pickle
from Token import Token

def merge_docs(doc_list):
    """
    Used for merging a few documents to one dictionary of tokens and one of documents
    :param doc_list: List of document objects
    :return: dictionary of tokens
    """
    tokens_dictionary = _create_tokens_dictionary(doc_list)
    documents_dictionary = _create_document_dictionary(doc_list)
    save_obj(tokens_dictionary, 'test tokens dict')
    save_obj(tokens_dictionary, 'test docs dict')
    # return tokens_dictionary

def _create_tokens_dictionary(doc_list):
    super_dict = {}
    for doc in doc_list:
        if hasattr(doc, 'tokens'):
            for key in doc.tokens:
                if key in super_dict:
                    super_dict[key].add_data(doc.tokens[key], doc.doc_num)
                else:
                    super_dict[key] = Token(key)
                    super_dict[key].add_data(doc.tokens[key], doc.doc_num)
    return super_dict

def _create_document_dictionary(doc_list):
    document_dictionary = {}

    for doc in doc_list:
        document_dictionary[doc.doc_num] = doc

    return document_dictionary


def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)