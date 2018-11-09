import pandas as pd
import numpy as np
import os
import multiprocessing as mp
import datetime
from nltk.tokenize import word_tokenize
from nltk.stem.porter import *
import json

class ReadFile:
    manager = ''
    q = ''
    pool = ''
    jobs = []

    def __init__(self, directory, manager, q, pool):
        self.directory = directory
        ReadFile.manager = manager
        ReadFile.q = q
        ReadFile.pool = pool
        # self.manager = mp.Manager()
        # self.q = self.manager.Queue()
        # self.pool = mp.Pool(mp.cpu_count() + 2)
        # self.jobs = []
        self.multiprocess = True

    def run_file_reader(self):
        start_time = datetime.datetime.now()
        self.read_directory(self.directory)
        # ReadFile.q.put(['kill'])
        # ReadFile.pool.close()
        ReadFile.pool.join()
        finish_time = datetime.datetime.now()
        print(finish_time - start_time)

    def read_directory(self, directory):
        for root, dirs, files in os.walk(r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\corpus'):
            for file in files:
                # path = directory + '\\' + file + '\\' + file
                path = os.path.join(root, file)
                print(path)
                if self.multiprocess:
                    job = ReadFile.pool.apply_async(self.read_file, path)
                    ReadFile.jobs.append(job)
                else:
                    self.read_file(path)
        ReadFile.pool.join()

    def read_file(self, file_path):
        print('File: ' + file_path)
        with open(file_path, 'r') as content_file:
            content = content_file.read()
            content = content.replace('\n', '')
            while(content is not ''):
                start = content.find('<DOC>') + 5
                finish = content.find('</DOC>')
                doc = content[start:finish]
                print(doc)
                if self.multiprocess:
                    job = ReadFile.pool.apply_async(ReadFile.Document, doc)  # Need to make sure this line works
                    ReadFile.jobs.append(job)
                else:
                    Document(doc)
                content = content[finish + 6:]
        ReadFile.pool.join()

class Document:
    # TODO: need to check if in every document those tags are in the same position
    def __init__(self, data):
        self.stem = PorterStemmer()
        self.orig_data = data
        self.doc_num = self.get_doc_param('DOCNO') # in the same location
        self.HT = self.get_doc_param('HT') # in the same location
        self.set_text_full_text()
        # print(self.text)
        dict_to_json = {}
        dict_to_json['doc_num'] = self.doc_num
        dict_to_json['HT'] = self.HT
        dict_to_json['orig_data'] = self.orig_data
        print(dict_to_json)
        with open('jsons\\' + self.doc_num + 'txt', 'w') as outfile:
            json.dump(dict_to_json, outfile)

    def get_doc_parameter(self, line, label):
        start_label = '<' + label + '>'
        start_index = line.find('<' + label + '>')
        end_index = line.find('</' + label + '>')
        return line[start_index + len(start_label):end_index].rstrip().lstrip()

    def set_text(self, data):
        start = -1
        finish = -1
        for i in range(0, len(data)):
            if (start == -1 and '<TEXT>' in data[i]) or ('[Text]' in data[i]):
                start = i + 1
            if '</TEXT>' in data[i]:
                finish = i
                break
        data[i] = data[i].replace('[Text]', '')
        data[i] = data[i].replace('<TEXT>', '')
        self.text = data[start:finish]

    def set_text_full_text(self):
        finish = self.orig_data.find('</TEXT>')
        start = self.orig_data.find('<TEXT>') + 6
        start_brackets = self.orig_data.find('[Text]') + 6
        if start > start_brackets:
            self.text = self.orig_data[start:finish]
        else:
            self.text = self.orig_data[start_brackets:finish]

    def get_doc_param(self, label):
        start_label = '<' + label + '>'
        start = self.orig_data.find(start_label)
        finish = self.orig_data.find('</' + label + '>')
        return self.orig_data[start + len(start_label):finish]


    def create_terms(self):
        if self.stem:
            self.terms = set(word_tokenize(self.text))
        else:
            self.terms = set(word_tokenize(self.text))

if __name__ == '__main__':
    manager = mp.Manager()
    q = manager.Queue()
    pool = mp.Pool()
    file = ReadFile(r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\corpus', manager, q, pool)
    file.multiprocess = True
    # file.read_directory('C:\\Chen\\BGU\\2019\\2018 - Semester A\\3. Information Retrival\\Engine\\corpus\\FB396001')
    file.run_file_reader()
    # Counter([stemmer.stem(word) for word in word_tokenize(data)])