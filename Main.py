import datetime
import os
import multiprocessing as mp
import Indexer
from ReadFile import ReadFile

def read_directory(directory, multiprocess):
    # file_reader = ReadFile(stem, write_to_disk, q)

    for root, dirs, files in os.walk(directory):
        # TODO: Read also stop_words.txt from this directory and forward list to parser init
        stop_words_list = read_stop_words_lines(directory) # TODO: Figure out what is this
        for file in files:
            path = os.path.join(root, file)
            if multiprocess:
                pool.apply_async(ReadFile, (stem, write_to_disk, q, path, stop_words_list))
            else:
                ReadFile(stem, write_to_disk, q, path, stop_words_list)

    q.put('last doc')

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

def indexer_listener(docs_per_merge=50):
    docs = []
    jobs = []

    count = 0
    '''listens for messages on the docs_queue, writes to file. '''
    with open('listener output.txt', 'w+') as file:
        while 1:
            doc = q.get()
            count += 1
            if parallel and count == docs_per_merge:
                count = 0
                docs.append(doc)
                job = pool.apply_async(Indexer.merge_docs, (docs,))
                jobs.append(job)
                docs = []
                continue
            elif count == docs_per_merge: # TODO: delete after done testing - just for non-parallel testing
                count = 0
                docs.append(doc)
                Indexer.merge_docs(docs)
                docs = []
                continue
            if str(doc) == 'last doc':
                job = pool.apply_async(Indexer.merge_docs, (docs,))
                jobs.append(job)
                print('last doc')
                break
            docs.append(doc)
            file.write("Indexer received doc: " + str(doc.doc_num) + '\n')

    for job in jobs:
        res = job.get()

    pool.close()
    pool.join()
    # TODO: call function that uses data here


if __name__ == '__main__':
    # Debug configs:
    single_file = True
    write_to_disk = False
    parallel = False
    stem = False
    Index = True

    manager = mp.Manager()
    q = manager.Queue()
    pool = mp.Pool()

    start_time = datetime.datetime.now()

    # Single file debug config
    if single_file:
        # file = ReadFile(r'C:\Users\Nitzan\Desktop\FB396001', parallel, stem, write_to_disk, q, pool)
        read_directory(directory=r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\test directory\LA test', multiprocess=parallel)
    else:
        # All files debug config
        # file = ReadFile(r'C:\Users\Nitzan\Desktop\100 file corpus', parallel)
        read_directory(directory=r'C:\Users\Nitzan\Desktop\entire corpus\corpus', multiprocess=parallel)

    if Index:
        indexer_listener(50)

    finish_time = datetime.datetime.now()
    print(finish_time - start_time)
    # Counter([stemmer.stem(word) for word in word_tokenize(data)]) - This is the stem and tokenizing test, keep this here plz