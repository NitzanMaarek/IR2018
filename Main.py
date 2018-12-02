import datetime
import os
import multiprocessing as mp
import Indexer
from ReadFile import ReadFile

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
                    if file_count == 400:
                        print('dumping files')
                        processed_docs, next_batch_num = dump_proceesed_docs_to_disk(jobs, batch_size, next_batch_num)
                        next_batch_num += 1
                        total_doc_count += processed_docs
                        jobs = []
                        file_count = 0
                else:
                    ReadFile(file, stem, write_to_disk, q, path, stop_words_list)

    processed_docs, next_batch_num = dump_proceesed_docs_to_disk(jobs, batch_size, next_batch_num)
    total_doc_count += processed_docs
    print('Until merge runtime: ' + str(datetime.datetime.now() - start_time))
    Indexer.merge_chunks('pickles\\', next_batch_num + 1, stem)
    print(total_doc_count)

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
    merge_jobs = []
    batch_count = next_batch_num
    for job in jobs:
        new_docs_num = job.get().doc_count
        doc_count += new_docs_num
        temp_doc_count += new_docs_num
        if temp_doc_count > batch_size:
            print('started batch num: ' + str(batch_count))
            job = pool.apply_async(batch_to_disk, (batch_size, batch_count, q))
            batch_count += 1
            merge_jobs.append(job)
            temp_doc_count -= batch_size

    print('started batch num: ' + str(batch_count))
    job = pool.apply_async(batch_to_disk, (temp_doc_count, batch_count, q))
    merge_jobs.append(job)

    for job in merge_jobs:
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
    stem = False
    Index = True

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