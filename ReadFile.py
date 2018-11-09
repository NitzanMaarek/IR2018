import pandas as pd
import numpy as np
import os
import multiprocessing as mp
import datetime
from nltk.tokenize import word_tokenize
from nltk.stem.porter import *
from collections import Counter
import itertools

class ReadFile:
    def __init__(self, directory):
        self.directory = directory
        self.manager = mp.Manager()
        self.q = self.manager.Queue()
        self.pool = mp.Pool(mp.cpu_count() + 2)
        self.jobs = []
        self.multiprocess = True

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
            path = directory + '\\' + filename
            if os.path.isdir(path):
                if self.multiprocess:
                    print('Directory: ' + path)
                    job = self.pool.apply_async(self.read_directory, path)
                    self.jobs.append(job)
                else:
                    self.read_directory(path)
            else:
                if self.multiprocess:
                    job = self.pool.apply_async(self.read_file, path)
                    self.jobs.append(job)
                else:
                    self.read_file(path)

    def read_file(self, file_path):
        print('File: ' + file_path)
        with open(file_path, 'r') as content_file:
            content = content_file.read()
            content = content.replace('\n', '')
            while(content is not ''):
                start = content.find('<DOC>') + 5
                finish = content.find('</DOC>')
                doc = content[start:finish]
                if self.multiprocess:
                    job = self.pool.apply_async(Document, doc)  # Need to make sure this line works
                    self.jobs.append(job)
                else:
                    Document(doc)
                content = content[finish:]


class Document:
    # TODO: need to check if in every document those tags are in the same position
    def __init__(self, data):
        self.stem = PorterStemmer()
        self.orig_data = data
        self.doc_num = self.get_doc_param('DOCNO') # in the same location
        self.HT = self.get_doc_param('HT') # in the same location
        self.set_text_full_text()
        print(self.text)


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
    file = ReadFile(r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\corpus')
    file.multiprocess = False
    file.read_directory('C:\\Chen\\BGU\\2019\\2018 - Semester A\\3. Information Retrival\\Engine\\corpus\\FB396001')
    # file.run_file_reader()

    # Counter([stemmer.stem(word) for word in word_tokenize(data)])