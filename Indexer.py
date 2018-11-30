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

# def _create_document_dictionary(doc_list):


# def write_dictionary_to_disk(d):
#     h = h5py.File('myfile.hdf5')
#     for k, v in d.items():
#         h.create_dataset('%k%s')