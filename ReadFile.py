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
                job = self.pool.apply_async(self.read_directory, filename)
                self.jobs.append(job)
            else:
                job = self.pool.apply_async(self.read_file, filename)
                self.jobs.append(job)

    def read_file(self, file_path):
        with open(file_path) as file:
            doc = []
            for line in file:
                if "<DOC>" in line:
                    line
                    doc = []
                elif "</DOC>" in line:
                    job = self.pool.apply_async(Document.__init__, doc) # Need to make sure this line works
                    self.jobs.append(job)
                else:
                    doc.append(line)

    # def parse_file(self, doc):


class Document:
    def __init__(self, data):
        print(data)
        self.doc_num = self.get_doc_parameter(data[1], 'DOCNO')
        self.HT = self.get_doc_parameter(data[2], 'HT')


    def get_doc_parameter(self, line, label):
        print(line)
        line.replace('<' + label + '>', '')
        line.replace('</' + label + '>', '')
        line.replace(' ', '')
        print(line)
        return line

if __name__ == '__main__':
    file = ReadFile('C:\\Chen\\BGU\\2019\\2018 - Semester A\\3. Information Retrival\\Engine\\test directory')
    file.run_file_reader()