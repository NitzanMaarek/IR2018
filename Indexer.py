# import h5py
from Token import Token

def merge_docs(doc_list):
    """
    Used for merging a few documents to one dictionary of tokens and one of documents
    :param doc_list: List of document objects
    :return: dictionary of tokens
    """
    tokens_dictionary = _create_tokens_dictionary(doc_list)
    documents_dictionary = {}

    return tokens_dictionary

def _create_tokens_dictionary(doc_list):
    keys_dict = _create_index_dictionary(doc_list)
    return _create_super_dictionary(doc_list, keys_dict)

def _create_index_dictionary(doc_list):
    keys_dict = {}
    for i, d in enumerate(doc_list):
        for key, value in d.tokens.items():
            if key in keys_dict:
                keys_dict[key].append(i)
            else:
                keys_dict[key] = [i]

    return keys_dict

def _create_super_dictionary(doc_list, keys_dict):
    super_dict = {}
    all_tokens_sorted = sorted(keys_dict)

    for token_name in all_tokens_sorted:
        token = Token(token_name)
        for i in keys_dict[token_name]:
            token.add_data(doc_list[i].tokens[token_name], doc_list[i].doc_num)
        super_dict[token_name] = token

    return super_dict

# def _create_document_dictinary(doc_list):



# def write_dictionary_to_disk(d):
#     h = h5py.File('myfile.hdf5')
#     for k, v in d.items():
#         h.create_dataset('%k%s')