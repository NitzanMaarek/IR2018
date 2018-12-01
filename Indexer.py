# import h5py
import pickle
from Token import Token
import string
import psutil
import os

def merge_docs(doc_list, batch_num):
    """
    Used for merging a few documents to one dictionary of tokens and one of documents
    :param doc_list: List of document objects
    :return: dictionary of tokens
    """
    # p = psutil.Process(os.getpid())
    # p.nice(psutil.HIGH_PRIORITY_CLASS)
    tokens_dictionary = _create_tokens_dictionary(doc_list)
    documents_dictionary = _create_document_dictionary(doc_list)
    new_write_dictionary_by_prefix(tokens_dictionary, batch_num)

def _create_tokens_dictionary(doc_list):
    """

    :param doc_list: Gets
    :return:
    """
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

def write_dictionary_by_prefix(dict, batch_num):
    small_letters = string.ascii_lowercase
    big_letters = string.ascii_uppercase
    for i, first_letter in enumerate(small_letters):
        for j, second_letter in enumerate(small_letters):
            prefix_combos = [first_letter + second_letter, big_letters[i] + second_letter, big_letters[i] + big_letters[j]]
            sliced_dict = slice_dict(dict, prefix_combos)
            save_obj(sliced_dict, prefix_combos[0], batch_num)

def slice_dict(dict, prefix_combos):
    return {k: v for k, v in dict.items() if k.startswith(str(prefix_combos[0])) or k.startswith(str(prefix_combos[1])) or k.startswith(str(prefix_combos[2]))}

def new_write_dictionary_by_prefix(dict, batch_num):
    sorted_keys = sorted(dict)
    temp_dict = {}
    temp_key_prefix = None
    for key in sorted_keys:
        lower_case_key = lower_case_word(key)
        # ['/', '\\', ':', '*', '?', '"', '>', '<', '|']
        if not temp_key_prefix is None:
            if key[0] in ['/', '\\', ':', '*', '?', '"', '>', '<', '|'] or (len(key) > 1 and key[1] in ['/', '\\', ':', '*', '?', '"', '>', '<', '|']):
                continue
            elif (key[0].isdigit() or key[0] == '$') and key[0] == temp_key_prefix[0]:
                temp_dict[key] = dict[key]
                continue
            elif temp_key_prefix == lower_case_key[:2]:
                temp_dict[key] = dict[key]
                continue
            else:
                if temp_key_prefix[0].isdigit():
                    save_obj(temp_dict, temp_key_prefix, batch_num)
                    temp_key_prefix = lower_case_key[0]
                else:
                    save_obj(temp_dict, temp_key_prefix, batch_num)
                    temp_key_prefix = lower_case_key[:2]
                temp_dict = {}
                temp_dict[key] = dict[key]
                continue
        if key[0].isdigit:
            temp_key_prefix = key[0]
        else:
            temp_key_prefix = lower_case_key[:2]
        temp_dict[key] = dict[key]

def save_obj(obj, name, batch_num):
    with open('pickles\\' + name + '_' + str(batch_num) + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open('pickles\\' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def lower_case_word(token):
    """
    method checks if token is an alphabetical word. If so make it lower case
    :param token: string
    :return: if word, then same word in lower case, otherwise same token
    """
    chars_list = []    #list of strings to join after
    if token is not None:
        for char in token:
            char_int_rep = ord(char)
            if 65 <= char_int_rep <= 90:     #if char is UPPER case, make it lower case
                chars_list.append(chr(char_int_rep + 32))
            elif 97 <= char_int_rep <= 122:     #if char is not a letter then abort and return original token.
                chars_list.append(char)
            else:
                return token
        return ''.join(chars_list)
    return token
