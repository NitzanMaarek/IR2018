import datetime
import os
import multiprocessing as mp
from Indexer import Indexer
from Parse import Parse
from ReadFile import ReadFile

def read_directory(directory, multiprocess):
    jobs = []
    # file_reader = ReadFile(stem, write_to_disk, q)

    for root, dirs, files in os.walk(directory):
        # TODO: Read also stop_words.txt from this directory and forward list to parser init
        Parse.static_stop_words_list = read_stop_words_lines(directory) # TODO: Figure out what is this
        for file in files:
            path = os.path.join(root, file)
            if multiprocess:
                job = pool.apply_async(ReadFile, (stem, write_to_disk, q, path))
                jobs.append(job)
            else:
                ReadFile(stem, write_to_disk, q, path)

    for job in jobs:
        res = job.get()

    q.put('kill')

    pool.close()
    pool.join()

def read_stop_words_lines(directory):
    try:
        stop_words_list = []
        stop_words_file = open(directory + '\\' + 'stop_words.txt', 'r')
        for line in stop_words_file:
            if line[-1:] == '\n':
                line = line[:-1]
            if line.__contains__('\\'):     # TODO: Need to fix when there is \ in stopword
                line = line.replace('\\')
            stop_words_list.append(line)
        return stop_words_list
    except Exception as e:
        print(e)
        print('File not found: ' + directory + 'stop_words.txt')

if __name__ == '__main__':
    # Debug configs:
    single_file = True
    write_to_disk = False
    parallel = True
    stem = False
    Index = True

    manager = mp.Manager()
    q = manager.Queue()
    pool = mp.Pool()

    start_time = datetime.datetime.now()

    # put listener to work first
    if Index:
        indexer = Indexer('posting path', q)
        pool.apply_async(indexer.run_listener, )

    # Single file debug config
    if single_file:
        # file = ReadFile(r'C:\Users\Nitzan\Desktop\FB396001', parallel, stem, write_to_disk, q, pool)
        read_directory(directory=r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\test directory\100 files', multiprocess=parallel)
    else:
        # All files debug config
        read_directory(directory=r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\test directory\100 files', multiprocess=parallel)

    finish_time = datetime.datetime.now()
    print(finish_time - start_time)
    # Counter([stemmer.stem(word) for word in word_tokenize(data)]) - This is the stem and tokenizing test, keep this here plz