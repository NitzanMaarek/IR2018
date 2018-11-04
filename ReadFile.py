import pandas as pd
import numpy as np
import os
import multiprocessing as mp
import datetime

class ReadFile:
    def __init__(self, directory):
        self.directory = directory
        self.manager = mp.Manager()
        self.q = self.manager.Queue()
        self.pool = mp.Pool(mp.cpu_count() + 2)
        self.jobs = []
        self.multiprocess = False

    def run_file_reader(self):
        start_time = datetime.datetime.now()
        self.read_directory(self.directory)
        self.q.put(['kill'])
        self.pool.close()
        self.pool.join()
        finish_time = datetime.datetime.now()
        print(finish_time - start_time)

    def read_directory(self, directory):
        for filename in os.listdir(directory):
            if os.path.isdir(filename):
                if self.multiprocess:
                    job = self.pool.apply_async(self.read_directory, directory + '\\' + filename)
                    self.jobs.append(job)
                else:
                    self.read_directory(directory + '\\' + filename)
            else:
                if self.multiprocess:
                    job = self.pool.apply_async(self.read_file, directory + '\\' + filename)
                    self.jobs.append(job)
                else:
                    self.read_file(directory + '\\' + filename)

    def read_file(self, file_path):
        with open(file_path) as file:
            doc = []
            for line in file:
                if "<DOC>" in line:
                    doc = []
                elif "</DOC>" in line:
                    if self.multiprocess:
                        job = self.pool.apply_async(Document.__init__, doc) # Need to make sure this line works
                        self.jobs.append(job)
                    else:
                        Document(doc)
                elif line is not '\n':
                    line = line.replace('\n', '')
                    doc.append(line)

    # def parse_file(self, doc):


class Document:
    def __init__(self, data):
        print(data)
        self.doc_num = self.get_doc_parameter(data[0], 'DOCNO')
        self.HT = self.get_doc_parameter(data[1], 'HT')


    def get_doc_parameter(self, line, label):
        line = line.replace('<' + label + '>', '')
        line = line.replace('</' + label + '>', '')
        line = line.replace(' ', '')
        return line

if __name__ == '__main__':
    # list = []
    # with open('C:\\Chen\\BGU\\2019\\2018 - Semester A\\3. Information Retrival\\Engine\\test directory\\testfile.txt') as file_test:
    #     for line in fiC>" in line:
    #         #     print(line)
    #         if line is not '\n':
    #             line = line.replace('\n', '')
    #             list.append(line)
    # for line in list:le_test:
    #         # if "<DO
    #     print(list)
    file = ReadFile('C:\\Chen\\BGU\\2019\\2018 - Semester A\\3. Information Retrival\\Engine\\test directory')
    file.run_file_reader()