import Preferences
import pickle
from Token import Token
import os

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
    Creates a dictionary for all the unique tokens in the current batch and for all the documents.
    The dictionary is created from a list of document objects which might have the duplicate terms.
    :param doc_list: Gets
    :return: merged dictionary
    """

    tokens_dict = {}
    pointers_dictionary = {}
    current_length = 0

    with open(run_time_directory + 'document posting\\' + 'doc_posting_' +  str(batch_num), 'w') as file:

        for doc in doc_list:
            # Adding doc to posting
            doc.set_pointer(batch_num, current_length)
            doc_string = doc.write_to_disk_string() + '\n'
            file.write(doc_string)
            pointers_dictionary[doc.doc_num] = current_length
            doc_pointer = str(batch_num) + ' ' + str(current_length)
            current_length = len(doc_string) + 1

            # Merging tokens
            if hasattr(doc, 'tokens'):
                    for key in doc.tokens:
                        if key in tokens_dict:
                            tokens_dict[key].add_data(doc_pointer, doc.tokens[key], doc.doc_num)
                        else:
                            tokens_dict[key] = Token(key)
                            tokens_dict[key].add_data(doc_pointer, doc.tokens[key], doc.doc_num)
    return tokens_dict

def write_dictionary_by_prefix(dict, batch_num):
    """
    Writes to the disk all the values in the given dictionary by their 2 letters prefix or the first number
    :dict: the given dictionary
    :param batch_num: added prefix so we won't write over different batches
    """
    sorted_keys = sorted(dict)
    temp_dict = {}
    temp_key_prefix = None
    for key in sorted_keys:
        lower_case_key = lower_case_word(key)
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
        if key[0].isdigit():
            temp_key_prefix = key[0]
        else:
            temp_key_prefix = lower_case_key[:2]
        temp_dict[key] = dict[key]

    # Writing the last dictionary to the memory:
    save_obj(temp_dict, temp_key_prefix, batch_num)

def save_obj(obj, name, batch_num):
    with open(run_time_directory + 'pickles\\' + name + '_' + str(batch_num) + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    file_name = run_time_directory + 'pickles\\' + name + '.pkl'
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
            elif 97 <= char_int_rep <= 122:     #if char is not a letter then abort and return original token.
                chars_list.append(char)
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

def merge_chunks(chunks_directory, num_of_chunks, stem_flag):
    """
    Method merges chunks into one file, i.e: aa0, aa1....aa(n-1) -> single aa posting file.
    :param chunks_path: directory with all chunks in it
    :param num_of_chunks: total number of chunks
    """

    if chunks_directory is None or num_of_chunks == 0:
        return None

    prefix_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'ag', 'ah', 'ai', 'aj', 'ak', 'al', 'am', 'an', 'ao', 'ap', 'aq', 'ar', 'as', 'at', 'au', 'av', 'aw', 'ax', 'ay', 'az', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'bg', 'bh', 'bi', 'bj', 'bk', 'bl', 'bm', 'bn', 'bo', 'bp', 'bq', 'br', 'bs', 'bt', 'bu', 'bv', 'bw', 'bx', 'by', 'bz', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 'cg', 'ch', 'ci', 'cj', 'ck', 'cl', 'cm', 'cn', 'co', 'cp', 'cq', 'cr', 'cs', 'ct', 'cu', 'cv', 'cw', 'cx', 'cy', 'cz', 'da', 'db', 'dc', 'dd', 'de', 'df', 'dg', 'dh', 'di', 'dj', 'dk', 'dl', 'dm', 'dn', 'do', 'dp', 'dq', 'dr', 'ds', 'dt', 'du', 'dv', 'dw', 'dx', 'dy', 'dz', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'eg', 'eh', 'ei', 'ej', 'ek', 'el', 'em', 'en', 'eo', 'ep', 'eq', 'er', 'es', 'et', 'eu', 'ev', 'ew', 'ex', 'ey', 'ez', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff', 'fg', 'fh', 'fi', 'fj', 'fk', 'fl', 'fm', 'fn', 'fo', 'fp', 'fq', 'fr', 'fs', 'ft', 'fu', 'fv', 'fw', 'fx', 'fy', 'fz', 'ga', 'gb', 'gc', 'gd', 'ge', 'gf', 'gg', 'gh', 'gi', 'gj', 'gk', 'gl', 'gm', 'gn', 'go', 'gp', 'gq', 'gr', 'gs', 'gt', 'gu', 'gv', 'gw', 'gx', 'gy', 'gz', 'ha', 'hb', 'hc', 'hd', 'he', 'hf', 'hg', 'hh', 'hi', 'hj', 'hk', 'hl', 'hm', 'hn', 'ho', 'hp', 'hq', 'hr', 'hs', 'ht', 'hu', 'hv', 'hw', 'hx', 'hy', 'hz', 'ia', 'ib', 'ic', 'id', 'ie', 'if', 'ig', 'ih', 'ii', 'ij', 'ik', 'il', 'im', 'in', 'io', 'ip', 'iq', 'ir', 'is', 'it', 'iu', 'iv', 'iw', 'ix', 'iy', 'iz', 'ja', 'jb', 'jc', 'jd', 'je', 'jf', 'jg', 'jh', 'ji', 'jj', 'jk', 'jl', 'jm', 'jn', 'jo', 'jp', 'jq', 'jr', 'js', 'jt', 'ju', 'jv', 'jw', 'jx', 'jy', 'jz', 'ka', 'kb', 'kc', 'kd', 'ke', 'kf', 'kg', 'kh', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'kp', 'kq', 'kr', 'ks', 'kt', 'ku', 'kv', 'kw', 'kx', 'ky', 'kz', 'la', 'lb', 'lc', 'ld', 'le', 'lf', 'lg', 'lh', 'li', 'lj', 'lk', 'll', 'lm', 'ln', 'lo', 'lp', 'lq', 'lr', 'ls', 'lt', 'lu', 'lv', 'lw', 'lx', 'ly', 'lz', 'ma', 'mb', 'mc', 'md', 'me', 'mf', 'mg', 'mh', 'mi', 'mj', 'mk', 'ml', 'mm', 'mn', 'mo', 'mp', 'mq', 'mr', 'ms', 'mt', 'mu', 'mv', 'mw', 'mx', 'my', 'mz', 'na', 'nb', 'nc', 'nd', 'ne', 'nf', 'ng', 'nh', 'ni', 'nj', 'nk', 'nl', 'nm', 'nn', 'no', 'np', 'nq', 'nr', 'ns', 'nt', 'nu', 'nv', 'nw', 'nx', 'ny', 'nz', 'oa', 'ob', 'oc', 'od', 'oe', 'of', 'og', 'oh', 'oi', 'oj', 'ok', 'ol', 'om', 'on', 'oo', 'op', 'oq', 'or', 'os', 'ot', 'ou', 'ov', 'ow', 'ox', 'oy', 'oz', 'pa', 'pb', 'pc', 'pd', 'pe', 'pf', 'pg', 'ph', 'pi', 'pj', 'pk', 'pl', 'pm', 'pn', 'po', 'pp', 'pq', 'pr', 'ps', 'pt', 'pu', 'pv', 'pw', 'px', 'py', 'pz', 'qa', 'qb', 'qc', 'qd', 'qe', 'qf', 'qg', 'qh', 'qi', 'qj', 'qk', 'ql', 'qm', 'qn', 'qo', 'qp', 'qq', 'qr', 'qs', 'qt', 'qu', 'qv', 'qw', 'qx', 'qy', 'qz', 'ra', 'rb', 'rc', 'rd', 're', 'rf', 'rg', 'rh', 'ri', 'rj', 'rk', 'rl', 'rm', 'rn', 'ro', 'rp', 'rq', 'rr', 'rs', 'rt', 'ru', 'rv', 'rw', 'rx', 'ry', 'rz', 'sa', 'sb', 'sc', 'sd', 'se', 'sf', 'sg', 'sh', 'si', 'sj', 'sk', 'sl', 'sm', 'sn', 'so', 'sp', 'sq', 'sr', 'ss', 'st', 'su', 'sv', 'sw', 'sx', 'sy', 'sz', 'ta', 'tb', 'tc', 'td', 'te', 'tf', 'tg', 'th', 'ti', 'tj', 'tk', 'tl', 'tm', 'tn', 'to', 'tp', 'tq', 'tr', 'ts', 'tt', 'tu', 'tv', 'tw', 'tx', 'ty', 'tz', 'ua', 'ub', 'uc', 'ud', 'ue', 'uf', 'ug', 'uh', 'ui', 'uj', 'uk', 'ul', 'um', 'un', 'uo', 'up', 'uq', 'ur', 'us', 'ut', 'uu', 'uv', 'uw', 'ux', 'uy', 'uz', 'va', 'vb', 'vc', 'vd', 've', 'vf', 'vg', 'vh', 'vi', 'vj', 'vk', 'vl', 'vm', 'vn', 'vo', 'vp', 'vq', 'vr', 'vs', 'vt', 'vu', 'vv', 'vw', 'vx', 'vy', 'vz', 'wa', 'wb', 'wc', 'wd', 'we', 'wf', 'wg', 'wh', 'wi', 'wj', 'wk', 'wl', 'wm', 'wn', 'wo', 'wp', 'wq', 'wr', 'ws', 'wt', 'wu', 'wv', 'ww', 'wx', 'wy', 'wz', 'xa', 'xb', 'xc', 'xd', 'xe', 'xf', 'xg', 'xh', 'xi', 'xj', 'xk', 'xl', 'xm', 'xn', 'xo', 'xp', 'xq', 'xr', 'xs', 'xt', 'xu', 'xv', 'xw', 'xx', 'xy', 'xz', 'ya', 'yb', 'yc', 'yd', 'ye', 'yf', 'yg', 'yh', 'yi', 'yj', 'yk', 'yl', 'ym', 'yn', 'yo', 'yp', 'yq', 'yr', 'ys', 'yt', 'yu', 'yv', 'yw', 'yx', 'yy', 'yz', 'za', 'zb', 'zc', 'zd', 'ze', 'zf', 'zg', 'zh', 'zi', 'zj', 'zk', 'zl', 'zm', 'zn', 'zo', 'zp', 'zq', 'zr', 'zs', 'zt', 'zu', 'zv', 'zw', 'zx', 'zy', 'zz']
    stem_addition_for_prefix = ''
    stem_addition_for_files = ''
    if stem_flag:
        stem_addition_for_prefix = '_stem'
        stem_addition_for_files = 's'

    for prefix in prefix_list:
        list_chunk_dictionaries = get_list_chunks_dictionary(num_of_chunks, prefix, stem_addition_for_prefix)
        if len(list_chunk_dictionaries) == 0:       # No terms in this prefix.
            continue
        merged_prefix_dictionary = merge_tokens_dictionaries(list_chunk_dictionaries)  #TODO: change function here to one that really merges dicitonaries
        sorted_terms = sorted(merged_prefix_dictionary)
        # Write dictionary as posting file
        dictionary_file_name = ''.join([run_time_directory , stem_addition_for_files, 'd_', prefix])     # d_aa or sd_aa for dictionary aa or stemmed aa respectively
        posting_file_name = ''.join([run_time_directory, 'terms posting\\', stem_addition_for_files, 'tp_', prefix])        # tp_aa or stp_aa for TERM posting or stemmed posting for aa respectively
        seek_offset = 0
        with open(dictionary_file_name, 'w') as d, open (posting_file_name, 'w') as tp:
            for term in sorted_terms:
                term_record = merged_prefix_dictionary[term]     #TODO: remove casting
                term_documents_attributes = term_record.create_string_from_doc_dictionary() #TODO: Need to add pointer to documents to attributes.
                str_for_posting = ''.join([term, ' ', term_documents_attributes, '\n'])
                # string is: term <doc_id tf first_position_in_doc doc_pointer> <doc_id tf first_position_in_doc doc_pointer>...
                str_for_dictionary = ''.join([term, ' <', str(merged_prefix_dictionary[term].df), ' ', posting_file_name, ' ', str(seek_offset), '>\n'])
                seek_offset += len(str_for_posting)
                # string is term df posting_file_name seek_position(pointer to line of term)
                d.write(str_for_dictionary)
                tp.write(str_for_posting)


def create_prefix_posting(prefix, file_name_list, q):

    terms_dictionary = {}
    pickle_dictionaries = get_pickles_by_file_names(file_name_list)
    merged_prefix_dictionary = merge_tokens_dictionaries(pickle_dictionaries) # Need to return this
    sorted_terms = sorted(merged_prefix_dictionary)

    if Preferences.stem:
        stem_addition_for_posting = '_stem'
        stem_addition_for_files = 's'
    else:
        stem_addition_for_posting = ''
        stem_addition_for_files = ''

    # dictionary_file_name = ''.join(preferences.main_directory + 'main_dictionary')  # d_aa or sd_aa for dictionary aa or stemmed aa respectively
    posting_file_name = ''.join([Preferences.main_directory, 'terms posting\\', stem_addition_for_files, 'tp_',
                                 prefix])  # tp_aa or stp_aa for TERM posting or stemmed posting for aa respectively
    seek_offset = 0
    with open(posting_file_name, 'w') as tp:
        for term in sorted_terms:
            terms_dictionary[term] = seek_offset
            str_for_posting = ''.join([term, ' ', merged_prefix_dictionary[term].create_string_from_doc_dictionary(), '\n'])
            seek_offset += len(str_for_posting) + 1
            tp.write(str_for_posting)

    return merged_prefix_dictionary, prefix

def get_pickles_by_file_names(file_name_list):
    dictionaries = []
    for file in file_name_list:
        dictionaries.append(load_obj(file))
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