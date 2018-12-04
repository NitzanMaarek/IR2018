import datetime
import os
import multiprocessing as mp
import Indexer
from ReadFile import ReadFile
import Preferences

def read_directory(directory, multiprocess, batch_size=20000):
    """
    Iterating over files in a directory and opening ReadFile object for each one.
    The ReadFile object processes the file and creates Document objects.
    After finishing a certain amount of Documents the function writes the data to the disk.
    :param directory: directory to read path
    :param multiprocess: multiprocess or sequential
    :param batch_size: after how many files write the data to the disk
    """
    jobs = []
    file_count = 0
    total_doc_count = 0
    next_batch_num = 0
    for root, dirs, files in os.walk(directory):
        # TODO: Read also stop_words.txt from this directory and forward list to parser init
        stop_words_list = read_stop_words_lines(directory) # TODO: Figure out what is this
        for file in files:
            if not file == 'stop_words.txt':
                path = os.path.join(root, file)
                if multiprocess:
                    job = pool.apply_async(ReadFile, (file, stem, write_to_disk, q, path, stop_words_list))
                    jobs.append(job)
                    file_count += 1
                    if file_count == 300:
                        print('dumping files')
                        processed_docs, next_batch_num = dump_proceesed_docs_to_disk(jobs, batch_size, next_batch_num)
                        next_batch_num += 1
                        total_doc_count += processed_docs
                        jobs = []
                        file_count = 0
                else:
                    ReadFile(file, stem, write_to_disk, q, path, stop_words_list)

    if len(jobs) > 0:
        processed_docs, next_batch_num = dump_proceesed_docs_to_disk(jobs, batch_size, next_batch_num)
        total_doc_count += processed_docs
    print('total docs: ' + str(total_doc_count))
    print('Until merge runtime: ' + str(datetime.datetime.now() - start_time))
    merge_pickles_to_terms_dictionary()
    # terms_dictionary = merge_tokens_dictionary()
    # Indexer.save_obj_dictionary(terms_dictionary, 'main terms dictionary')
    # test = Indexer.load_obj_dictionary('main terms dictionary.pkl')
    # print(test)

def merge_tokens_dictionary():
    terms_dict = {}
    for file in os.listdir(Preferences.main_directory + 'dictionary\\'):
        terms_dict = {**terms_dict, **Indexer.load_obj_dictionary(file)}
    return terms_dict

def dump_proceesed_docs_to_disk(jobs, batch_size, next_batch_num):
    """
    Writing the processed data to the disk before reading more files
    :param jobs: jobs of documents
    :param batch_size: how many files to write to disk per batch
    :param next_batch_num: next batch index
    :return: count of how many documents we processed and the number of writing to disk batches we did
    """
    doc_count = 0
    temp_doc_count = 0
    batch_jobs = []
    batch_count = next_batch_num
    for job in jobs:
        new_docs_num = job.get().doc_count
        doc_count += new_docs_num
        temp_doc_count += new_docs_num
        if temp_doc_count > batch_size:
            print('started batch num: ' + str(batch_count))
            job = pool.apply_async(batch_to_disk, (batch_size, batch_count, q))
            batch_count += 1
            batch_jobs.append(job)
            temp_doc_count -= batch_size

    print('started batch num: ' + str(batch_count))
    job = pool.apply_async(batch_to_disk, (temp_doc_count, batch_count, q))
    batch_jobs.append(job)

    for job in batch_jobs:
        res = job.get()

    return doc_count, batch_count

def batch_to_disk(batch_size, batch_num, q):
    """
    Writing the next given amount of documents to the disk
    :param batch_size: how many documents should we write to the disk
    :param batch_num: batch serial number
    :param q: queue from which we retrieve the Document objects from
    """
    docs = []
    count = 0
    while batch_size > count:
        docs.append(q.get())
        count += 1
    Indexer.write_docs_list_to_disk(docs, batch_num)

def create_tokens_posting():
    partial_terms_dictionary = {}
    prefix_tokens_dictionaries = get_list_of_files_by_prefix()
    posting_jobs = []
    counter = 0
    batch_counter = 0
    for prefix in prefix_tokens_dictionaries:
        if counter < Preferences.posting_files_per_batch:
            counter += 1
            job = pool.apply_async(Indexer.create_prefix_posting, (prefix, prefix_tokens_dictionaries[prefix], q))
            posting_jobs.append(job)

            if counter == Preferences.posting_files_per_batch:
                counter = 0
                for job in posting_jobs:
                    prefix_dict, prefix = job.get()
                    partial_terms_dictionary[prefix] = prefix_dict
                Indexer.save_obj_dictionary(partial_terms_dictionary, 'terms_dictionary', batch_counter)
                partial_terms_dictionary = {}
                batch_counter += 1

    # TODO: check if we need to get back the dictionary

# Test
def merge_pickles_to_terms_dictionary():
    prefix_tokens_dictionaries = get_list_of_files_by_prefix()
    posting_jobs = []
    for key in prefix_tokens_dictionaries.keys():
        job = pool.apply_async(Indexer.create_prefix_posting, (key, prefix_tokens_dictionaries[key]))
        posting_jobs.append(job)

    for job in posting_jobs:
        job.get()

def get_list_of_files_by_prefix():
    list_of_files_by_prefix = {}

    for file in os.listdir(Preferences.main_directory + 'pickles\\'):
        prefix = file[:2]
        if not prefix in list_of_files_by_prefix:
            list_of_files_by_prefix[prefix] = []
        list_of_files_by_prefix[prefix].append(file[:-4])# Need to trim the last 4 chars to remove the suffix

    return list_of_files_by_prefix

def read_stop_words_lines(directory):
    try:
        stop_words_list = {}
        stop_words_file = open(directory + '\\' + 'stop_words.txt', 'r')
        for line in stop_words_file:
            if line[-1:] == '\n':
                line = line[:-1]
            if line.__contains__('\\'):     # TODO: Need to fix when there is \ in stopword
                line = line.replace('\\')
            stop_words_list[line] = 1
        return stop_words_list
    except Exception as e:
        print(e)
        print('File not found: ' + directory + 'stop_words.txt')


if __name__ == '__main__':
    # Debug configs:
    single_file = True
    write_to_disk = False
    parallel = True
    stem = Preferences.stem
    Index = True

    main_directory = Preferences.main_directory

    manager = mp.Manager()
    q = manager.Queue()
    pool = mp.Pool(processes=mp.cpu_count())

    start_time = datetime.datetime.now()

    # Single file debug config
    if single_file:
        # file = ReadFile(r'C:\Users\Nitzan\Desktop\FB396001', parallel, stem, write_to_disk, q, pool)
        read_directory(directory=r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\test directory\10 files', multiprocess=parallel, batch_size=20000)
    else:
        # All files debug config
        # file = ReadFile(r'C:\Users\Nitzan\Desktop\100 file corpus', parallel)
        read_directory(directory=r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\corpus', multiprocess=parallel)

    finish_time = datetime.datetime.now()
    print(finish_time - start_time)