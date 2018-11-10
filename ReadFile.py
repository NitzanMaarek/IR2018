import pandas as pd
import numpy as np
import os
import multiprocessing as mp
import datetime
from nltk.tokenize import word_tokenize
from nltk.stem.porter import *
import json

class ReadFile:
    def __init__(self, directory, multiprocess, stem):
        self.directory = directory
        self.multiprocess = multiprocess
        self.stem = stem

    def run_file_reader(self):
        start_time = datetime.datetime.now()
        self.read_directory_fixed_mp(self.directory)
        finish_time = datetime.datetime.now()
        print(finish_time - start_time)

    def read_directory(self, directory):
        for root, dirs, files in os.walk(r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\corpus'):
            for file in files:
                # path = directory + '\\' + file + '\\' + file
                path = os.path.join(root, file)
                # print(path)
                if self.multiprocess:
                    job = ReadFile.pool.apply_async(self.read_file_lines, path)
                    ReadFile.jobs.append(job)
                else:
                    self.read_file_lines(path)
        ReadFile.pool.join()

    def read_directory_fixed_mp(self, directory):
        manager = mp.Manager()
        q = manager.Queue()
        pool = mp.Pool()
        jobs = []

        for root, dirs, files in os.walk(directory):
            for file in files:
                # path = directory + '\\' + file + '\\' + file
                path = os.path.join(root, file)
                # print(path)
                if self.multiprocess:
                    job = pool.apply_async(self.read_file_lines, (path, q))
                    jobs.append(job)
                else:
                    self.read_file_lines(path)

        for job in jobs:
            res = job.get()
            # print(res)

        # q.put(['kill'])
        #
        # while 1:
        #     res = q.get()
        #     # print(res)
        #     if res is 'kill':
        #         break

        pool.close()
        pool.join()


    def read_file_lines(self, file_path, q):
        # with open(file_path, 'r') as lines:
        try:
            lines = open(file_path, 'r').readlines()
            for i, line in enumerate(lines, start=0):
                # print(line)
                if "<DOC>" in line:
                    start = i
                elif "</DOC>" in line:
                    if False:
                        job = self.pool.apply_async(Document.__init__, doc, self.stem)  # Need to make sure this line works
                        self.jobs.append(job)
                    else:
                        Document(lines[start + 1 : i - 1], self.stem ,q)
            # q.put(file_path)
        except:
            print(file_path)
        return file_path

    def read_file_full(self, file_path):
        # print('File: ' + file_path)
        with open(file_path, 'r') as content_file:
            try:
                content = content_file.read()
                content = content.replace('\n', '')
                while(content is not ''):
                    start = content.find('<DOC>') + 5
                    finish = content.find('</DOC>')
                    doc = content[start:finish]
                    # print(doc)
                    if self.multiprocess:
                        job = pool.apply_async(Document, doc, self.stem)  # Need to make sure this line works
                        # jobs.append(job)
                    else:
                        Document(doc)
                    content = content[finish + 6:]
            except:
                print(file_path)

class Document:
    def __init__(self, data, stem, q):
        self.stem = stem
        self.doc_num = self.get_doc_parameter_lines(data[0], 'DOCNO')
        # print(self.doc_num)
        self.HT = self.get_doc_parameter_lines(data[1], 'HT')

        start = -1
        finish = -1
        for i in range(0, len(data)):
            if 'DATE1' in data[i]:
                self.date = self.get_doc_parameter_lines(data[i], 'DATE1')
            if (start == -1 and '<TEXT>' in data[i]) or ('[Text]' in data[i]):
                start = i + 1
            if '</TEXT>' in data[i]:
                finish = i
                break

        data[i] = data[i].replace('[Text]', '')
        data[i] = data[i].replace('<TEXT>', '')
        self.text = data[start + 6:finish]

        dict_to_json = {}
        dict_to_json['doc_num'] = self.doc_num
        dict_to_json['HT'] = self.HT
        dict_to_json['orig_data'] = data
        # q.put(self.doc_num)
        # print(self.doc_num)
        # with open('C:\\Chen\\BGU\\2019\\2018 - Semester A\\3. Information Retrival\\Engine\\jsons\\' + self.doc_num + '.txt', 'w') as outfile:
        #     json.dump(dict_to_json, outfile)

    # TODO: need to check if in every document those tags are in the same position
    # def __init__(self, data): # full
    #     self.stem = PorterStemmer()
    #     self.orig_data = data
    #     self.doc_num = self.get_doc_param('DOCNO') # in the same location
    #     self.HT = self.get_doc_param('HT') # in the same location
    #     self.set_text_lines(data)
    #     dict_to_json = {}
    #     dict_to_json['doc_num'] = self.doc_num
    #     dict_to_json['HT'] = self.HT
    #     dict_to_json['orig_data'] = self.orig_data
    #     with open('C:\\Chen\\BGU\\2019\\2018 - Semester A\\3. Information Retrival\\Engine\\jsons\\' + self.doc_num + '.txt', 'w') as outfile:
    #         json.dump(dict_to_json, outfile)

    def set_text_lines(self, data): # No usage
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

    def get_doc_parameter_lines(self, line, label):
        start_label = '<' + label + '>'
        start_index = line.find('<' + label + '>')
        end_index = line.find('</' + label + '>')
        return line[start_index + len(start_label):end_index].rstrip().lstrip()

    def set_text_full_text(self):
        finish = self.orig_data.find('</TEXT>')
        start = self.orig_data.find('<TEXT>') + 6
        start_brackets = self.orig_data.find('[Text]') + 6
        if start > start_brackets:
            self.text = self.orig_data[start:finish]
        else:
            self.text = self.orig_data[start_brackets:finish]

    def get_doc_param_fulll(self, label):
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
    # All files debug config
    file = ReadFile(r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\corpus', True, False)
    file.run_file_reader()

    # Single file debug config
    # file = ReadFile(r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\corpus', False, True)
    # file.read_directory_fixed_mp(r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\test directory')
    # Counter([stemmer.stem(word) for word in word_tokenize(data)])