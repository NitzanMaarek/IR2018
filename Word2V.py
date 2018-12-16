import os
import multiprocessing as mp

from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Word2Vec
from ReadFile import ReadFile

class Word2V:

    def __init__(self, texts):
        path = get_tmpfile("word2vec.model")
        # list_of_lists = read_text_from_dir()
        model = Word2Vec(texts, size=100, window=5, min_count=1, workers=4)
        model.save("word2vec.model")

        # vector = model.wv['paper']
        # print(vector)


    def continue_training(self, texts):
        model = Word2Vec.load("word2vec.model")
        model.train(texts, total_examples=1, epochs=1)


def read_text_from_dir(main_dir, directory, multiprocess, batch_size=20000, stem=False):
    jobs = []
    file_count = 0
    total_doc_count = 0
    next_batch_num = 0
    language_set = set()

    stop_words_list = read_stop_words_lines(directory)
    word2vec = None
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file == 'stop_words.txt':
                path = os.path.join(root, file)
                if multiprocess:
                    job = pool.apply_async(ReadFile, (file, q, path, stop_words_list, stem))
                    jobs.append(job)
                    file_count += 1
                    if file_count == 100:
                        processed_docs, next_batch_num, list_of_texts = dump_proceesed_docs_to_disk(main_dir,
                                                                                                           jobs,
                                                                                                           batch_size,
                                                                                                           next_batch_num,
                                                                                                           stem)
                        # language_set = language_set.union(partial_language_set)
                        next_batch_num += 1
                        total_doc_count += processed_docs
                        jobs = []
                        file_count = 0
                        first_list = list_of_texts[0]
                        # print(first_list)
                        if word2vec is None:
                            print("Initializing model")
                            word2vec = Word2V(first_list)
                            print("Model created. Now training model.")
                            start = 1
                        else:
                            start = 0
                        total_texts = len(list_of_texts)
                        if total_texts > start:
                            for i in range(start, total_texts):
                                print("Training iteration number: " + str(i) + " out of: " + str(total_texts))
                                word2vec.continue_training(list_of_texts[i])
                else:
                    ReadFile(file, q, path, stop_words_list, stem)

    word2vec = None
    if len(jobs) > 0:
        processed_docs, next_batch_num, list_of_texts = dump_proceesed_docs_to_disk(main_dir, jobs, batch_size,
                                                                                           next_batch_num, stem)
        # processed_docs, next_batch_num, partial_language_set = dump_proceesed_docs_to_disk(main_dir, jobs, batch_size,
        #                                                                                    next_batch_num, stem)
        # language_set = language_set.union(partial_language_set)

        total_doc_count += processed_docs
        first_list = list_of_texts[0]
        # print(first_list)
        print("Initializing model")
        word2vec = Word2V(first_list)
        print("Model created. Now training model.")
        total_texts = len(list_of_texts)
        if total_texts > 1:
            for i in range(1, total_texts):
                print("Training iteration number: " + str(i) + " out of: " + total_texts)
                word2vec.continue_training(list_of_texts[i])

# def train_model(model, list_of_texts):
#     first_list = list_of_texts[0]
#     # print(first_list)
#     print("Initializing model")
#     word2vec = Word2V(first_list)
#     print("Model created. Now training model.")
#     total_texts = len(list_of_texts)
#     if total_texts > 1:
#         for i in range(1, total_texts):
#             print("Training iteration number: " + str(i) + " out of: " + total_texts)
#             word2vec.continue_training(list_of_texts[i])


def dump_proceesed_docs_to_disk(main_dir, jobs, batch_size, next_batch_num, stem):
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
            # print('started batch num: ' + str(batch_count))
            job = pool.apply_async(batch_to_disk, (main_dir, batch_size, batch_count, q, stem))
            batch_count += 1
            batch_jobs.append(job)
            temp_doc_count -= batch_size

    # print('started batch num: ' + str(batch_count))
    job = pool.apply_async(batch_to_disk, (main_dir, temp_doc_count, batch_count, q, stem))
    batch_jobs.append(job)

    list_of_texts = []
    for job in batch_jobs:
        only_some_texts = job.get()
        list_of_texts.append(only_some_texts)



    # language_set = set()
    # for job in batch_jobs:
    #     partial_language_set = job.get()
    #     language_set = language_set.union(partial_language_set)

    return doc_count, batch_count, list_of_texts

def batch_to_disk(main_dir, batch_size, batch_num, q, stem):
    """
    Writing the next given amount of documents to the disk
    :param batch_size: how many documents should we write to the disk
    :param batch_num: batch serial number
    :param q: queue from which we retrieve the Document objects from
    """
    docs = []
    text_list = []
    count = 0
    languages_partial_set = set()
    while batch_size > count:
        doc = q.get()
        if hasattr(doc, 'language'):
            languages_partial_set.add(doc.language)
        if hasattr(doc, 'tokens'):
            if hasattr(doc, 'title'):
                terms = list(doc.tokens.keys())
                terms = terms + doc.title.split()
                text_list.append(terms)
            else:
                text_list.append(doc.tokens.keys())
        elif hasattr(doc, 'title'):
            text_list.append(doc.title)
        docs.append(doc)

        count += 1
    # ***** Changed by nitsan to debug ****
    return text_list
    # Indexer.write_docs_list_to_disk(main_dir, docs, batch_num, stem)
    # return languages_partial_set

def read_stop_words_lines(directory):
    """
    Reads stop words file
    :param directory: file location
    :return: returns list of stop words
    """
    try:
        stop_words_list = {}
        stop_words_file = open(directory + '\\' + 'stop_words.txt', 'r')
        for line in stop_words_file:
            if line[-1:] == '\n':
                line = line[:-1]
            if line.__contains__('\\'):
                line = line.replace('\\')
            stop_words_list[line] = 1
        return stop_words_list
    except Exception as e:
        print(e)
        print('File not found: ' + directory + 'stop_words.txt')



if __name__ == '__main__':

    manager = mp.Manager()
    q = manager.Queue()
    pool = mp.Pool(processes=mp.cpu_count())

    read_text_from_dir(main_dir='', directory=r'C:\Users\Nitzan\Desktop\IR 2018 files desktop\entire corpus\corpus', multiprocess=True, batch_size=20000, stem=False)