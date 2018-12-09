import Preferences
import pickle
from Token import Token
import os
from City import CityToken, CityIndexer
import codecs

run_time_directory = Preferences.main_directory

def write_docs_list_to_disk(doc_list, batch_num):
    """
    Used for merging a few documents to one dictionary of tokens and one of documents
    :param doc_list: List of document objects
    :return: dictionary of tokens
    """
    tokens_dictionary = create_merged_dictionary_and_doc_posting(doc_list, batch_num)
    write_dictionary_by_prefix(tokens_dictionary, batch_num)

def create_merged_dictionary_and_doc_posting(doc_list, batch_num):
    """
    Creates a dictionary for all the unique tokens that appeared in the documents of the current batch.
    The dictionary is created from a list of document objects which might have the duplicate terms.
    :param doc_list: receives a list of document objects after they have been parsed
    :return: merged tokens dictionary
    """

    tokens_dict = {}
    pointers_dictionary = {}
    cities_dict = {}
    rows_count = 0

    with open(run_time_directory + 'document posting\\' + 'doc_posting_' + str(batch_num), 'w') as file:

        for doc in doc_list:
            # Adding doc to posting
            doc.set_pointer(batch_num, rows_count)
            doc_string = doc.write_to_disk_string() + '\n'
            file.write(doc_string)
            pointers_dictionary[doc.doc_num] = rows_count
            doc_pointer = str(batch_num) + ' ' + str(rows_count)
            rows_count += 1

            if hasattr(doc, 'city'):
                city = doc.city
                if city in cities_dict:
                    cities_dict[city].add_data(doc_num=doc.doc_num, doc_pointer=doc_pointer)
                else:
                    cities_dict[city] = CityToken(city_name=city)
                    cities_dict[city].add_data(doc_num=doc.doc_num, doc_pointer=doc_pointer)

            # Merging tokens
            if hasattr(doc, 'tokens'):
                    for key in doc.tokens:
                        if key in tokens_dict:
                            if doc.tokens[key][0] == 0:
                                print('stop')
                            tokens_dict[key].add_data(doc_num=doc.doc_num, doc_pointer=doc_pointer, list=doc.tokens[key])
                        else:
                            if doc.tokens[key][0] == 0:
                                print('stop')
                            tokens_dict[key] = Token(key)
                            tokens_dict[key].add_data(doc_num=doc.doc_num, doc_pointer=doc_pointer, list=doc.tokens[key])

    save_obj(cities_dict, 'cities_dict', batch_num, 'cities')

    return tokens_dict

def write_dictionary_by_prefix(dict, batch_num):
    """
    Writes to the disk all the values in the given dictionary by their 2 letters prefix or the first number
    :dict: the given dictionary
    :param batch_num: added prefix so we won't write over different batches
    """
    sorted_keys = sorted(dict, key=lambda k: (k.upper(), k[0].islower()))
    temp_dict = {}
    temp_key_prefix = None
    cant_write_to_disk = ['/', '\\', ':', '*', '?', '"', '>', '<', '|']
    for key in sorted_keys:
        lower_case_key = lower_case_word(key)
        if not temp_key_prefix is None:
            if lower_case_key[0] in cant_write_to_disk or (len(lower_case_key) > 1 and key[1] in cant_write_to_disk):
                continue
            elif (lower_case_key[0].isdigit() or lower_case_key[0] == '$' or lower_case_key[0] == '%') and lower_case_key[0] == temp_key_prefix[0]:
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
        if lower_case_key[0].isdigit() or lower_case_key[0] == '$' or key[0] == '%':
            temp_key_prefix = lower_case_key[0]
        else:
            temp_key_prefix = lower_case_key[:2]
        temp_dict[key] = dict[key]

    # Writing the last dictionary to the memory:
    save_obj(temp_dict, temp_key_prefix, batch_num)

def save_obj(obj, name, batch_num='', directory='pickles'):
    """
    Saves object as a pickle in a given directory in the main directory
    :param obj: object to save
    :param name: name of the new file
    :param batch_num: batch name if we intend to save several files with the same name
    :param directory: directory in which we will save the file
    """
    if batch_num == '':
        file_name = run_time_directory + directory + '\\' + name + '.pkl'
    else:
        file_name = run_time_directory + directory + '\\' + name + '_' + str(batch_num) + '.pkl'
    with open(file_name, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name, directory='pickles'):
    """
    Loads an object which was saved as a pickle in one of the directories in the main directory
    :param name: name of the file
    :param directory: directory in which the file is in
    :return: the object
    """
    file_name = run_time_directory + directory + '\\' + name + '.pkl'
    if os.path.isfile(file_name):
        with open(file_name, 'rb') as f:
            return pickle.load(f)
    return None

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
            else:
                chars_list.append(char)
        return ''.join(chars_list)
    return token

def get_list_chunks_dictionary(num_of_chunks, prefix, stem_str):
    """
    reads all pickle files of given prefix and collects all dictionaries to a list
    :param num_of_chunks: number of chunks to collect
    :param prefix: prefix to pull
    :param stem_str: empty string if no use of stemming, otherwise equals
    :return: list of dictionaries of prefix
    """
    list_dictionaries = []
    for i in range(0,num_of_chunks):
        dict = load_obj(''.join([prefix, '_', str(i), stem_str]))
        if not dict == None:
            list_dictionaries.append(dict)
    return list_dictionaries


def create_prefix_posting(prefix, file_name_list, directory='pickles'):
    """
    Creates posting file to a given prefix and writes it to the disk as txt file
    The function also creates pickle file which contains the dictionary that was made for the posting file
    :param prefix: given prefix
    :param file_name_list: list of file names which contains the data that we make the posting from
    """

    pickle_dictionaries = get_pickles_by_file_names(file_name_list, directory)
    merged_prefix_dictionary = merge_tokens_dictionaries(pickle_dictionaries) # Need to return this
    sorted_terms = sorted(merged_prefix_dictionary, key=lambda k: (k.upper(), k[0].islower()))

    if Preferences.stem:
        stem_addition_for_posting = '_stem'
        stem_addition_for_files = 's'
    else:
        stem_addition_for_posting = ''
        stem_addition_for_files = ''

    posting_file_name = ''.join([Preferences.main_directory, 'terms posting\\', stem_addition_for_files, 'tp_',
                                 prefix])  # tp_aa or stp_aa for TERM posting or stemmed posting for aa respectively

    create_posting_file(sorted_terms, merged_prefix_dictionary, posting_file_name, prefix)

def create_posting_file(sorted_terms, merged_dict, posting_file_name, tag, save_directory='dictionary'):
    """
    Creates a posting file from sorted list of terms and dictionary with those term's tokens
    :param sorted_terms: list of terms
    :param merged_dict: dictionary which contains tokens objects of the sorted terms
    :param posting_file_name: name of the new posting file
    :param tag: if we want to add a tag to new file name
    :param save_directory: where to save the new file
    """
    terms_dictionary = {}
    last_seek_offset = 0
    seek_offset = 0
    posting_file = []
    last_term = ''

    for term in sorted_terms:
        if not last_term == '' and not last_term[0].isdigit() and term == lower_case_word(last_term):
            # Deleting the upper case token from all relevant locations
            upper_case_term = merged_dict.pop(last_term)
            terms_dictionary.pop(last_term)
            del posting_file[-1]
            # Merging tokens
            merged_dict[term].merge_tokens(upper_case_term)
            # Fixing the offset
            seek_offset = last_seek_offset

        # terms_dictionary[term] = merged_dict[term]
        if hasattr(merged_dict[term], 'tf'):
            terms_dictionary[term] = (seek_offset, merged_dict[term].df, merged_dict[term].tf)
        else:
            terms_dictionary[term] = (seek_offset, merged_dict[term].df)
        str_for_posting = ''.join([term, ' ', merged_dict[term].create_string_from_doc_dictionary()])
        last_seek_offset = seek_offset
        seek_offset += len(str_for_posting)
        posting_file.append(str_for_posting)
        last_term = term
    with codecs.open(posting_file_name, 'w', 'utf-8') as tp:
        tp.writelines(posting_file)

    save_obj(terms_dictionary, tag, directory=save_directory)

def get_pickles_by_file_names(file_name_list, directory='pickles'):
    """
    Loading and appending into list pickles which are dictionaries
    :param file_name_list: list of file names
    :return: list of dictionaries
    """
    dictionaries = []
    for file in file_name_list:
        dictionaries.append(load_obj(file, directory))
    return dictionaries

def merge_tokens_dictionaries(dictionaries_list):
    """
    A function that merges dictionaries with tokens
    :param dictionaries_list: a list of dictionaries with token objects
    :return: the merged tokens dictionary
    """
    merged_dict = {}
    for dict in dictionaries_list:
        for key in dict:
            if key in merged_dict:
                merged_dict[key].merge_tokens(dict[key])
            else:
                merged_dict[key] = dict[key]
    return merged_dict

def create_cities_posting(print_countries_num=False):
    """
    This function acts as a pipeline for creating the posting file of the cities
    Also saves a dictionary file for the cities.
    :param print_countries_num: if you want to print the number of different countries in the corpus
    """
    cities_index = {}
    cities_indexer = CityIndexer()
    cities_dictionaries = []
    for file in os.listdir(Preferences.main_directory + 'cities'):
        cities_dictionaries.append(load_obj(file[:-4], directory='cities'))

    merged_dict = merge_tokens_dictionaries(cities_dictionaries)

    index_counter = 0
    for city_name in merged_dict:
        attr = cities_indexer.get_city_attributes(city_name.lower())
        if not attr is None: # Don't save it as a city if its not a real city
            merged_dict[city_name].set_attr(attr)
            cities_index[city_name] = index_counter
            index_counter += 1

    sorted_terms = sorted(merged_dict, key=lambda k: (k.upper(), k[0].islower()))

    posting_file_name = Preferences.main_directory + 'cities\\cities posting'

    create_posting_file(sorted_terms, merged_dict, posting_file_name, 'cities', save_directory='cities')

    save_obj(obj=cities_index, name='cities dictionary', directory='cities')
    if print_countries_num:
        print('num of countries: ' + str(len(cities_indexer.countries)))