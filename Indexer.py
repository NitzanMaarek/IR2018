# import h5py
import pickle
from Token import Token
import string

def merge_docs(doc_list):
    """
    Used for merging a few documents to one dictionary of tokens and one of documents
    :param doc_list: List of document objects
    :return: dictionary of tokens
    """
    tokens_dictionary = _create_tokens_dictionary(doc_list)
    documents_dictionary = _create_document_dictionary(doc_list)
    write_dictionary_by_prefix(tokens_dictionary)

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

def write_dictionary_by_prefix(dict):
    small_letters = string.ascii_lowercase
    big_letters = string.ascii_uppercase
    for i, first_letter in enumerate(small_letters):
        for j, second_letter in enumerate(small_letters):
            prefix_combos = [first_letter + second_letter, big_letters[i] + second_letter, big_letters[i] + big_letters[j]]
            sliced_dict = slice_dict(dict, prefix_combos)
            save_obj(sliced_dict, prefix_combos[0])

def slice_dict(dict, prefix_combos):
    return {k: v for k, v in dict.items() if k.startswith(str(prefix_combos[0])) or k.startswith(str(prefix_combos[1])) or k.startswith(str(prefix_combos[2]))}

def save_obj(obj, name):
    with open('pickles\\' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open('pickles\\' + name + '.pkl', 'rb') as f:
        return pickle.load(f)