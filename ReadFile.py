import os
import multiprocessing as mp
import datetime
from Parse import Parse
from Indexer import Indexer
import json

class ReadFile:
    def __init__(self, directory, multiprocess, stem, write_to_disk):
        self.directory = directory
        self.multiprocess = multiprocess
        self.stem = stem
        self.write_to_disk = write_to_disk

    def run_file_reader(self):
        self.read_directory(self.directory)

    def read_directory(self, directory):
        manager = mp.Manager()
        q = manager.Queue()
        pool = mp.Pool()
        jobs = []

        for root, dirs, files in os.walk(directory):
            # TODO: Read also stop_words.txt from this directory and forward list to parser init
            Parse.static_stop_words_list = self.read_stop_words_lines(directory)
            for file in files:
                path = os.path.join(root, file)
                if self.multiprocess:
                    job = pool.apply_async(self.read_file_lines, (path, q))
                    jobs.append(job)
                else:
                    self.read_file_lines(path, q)

        for job in jobs:
            res = job.get()

        pool.close()
        pool.join()

    def read_stop_words_lines(self, directory):
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


    def read_file_lines(self, file_path, q):
        try:
            file = open(file_path, 'r')
            lines = file.readlines()
            for i, line in enumerate(lines, start=0):
                if "<DOC>" in line:
                    start = i
                elif "</DOC>" in line:
                    Document(lines[start + 1: i - 1], self.stem, q, self.write_to_disk)
            file.close()

        except Exception as e:
            print(e)
            print("Processing file not succeeded: " + file_path)
        return file_path


class Document:
    def __init__(self, data, stem, q, write_to_disk):
        self.stem = stem
        self.doc_num = self.get_doc_parameter(data[0], 'DOCNO')
        self.HT = self.get_doc_parameter(data[1], 'HT')
        self.write_to_disk = write_to_disk

        start = -1
        finish = -1
        for i in range(0, len(data)):
            if 'DATE1' in data[i]:
                self.date = self.get_doc_parameter(data[i], 'DATE1')
            if (start == -1 and '<TEXT>' in data[i]) or ('[Text]' in data[i]):
                self.doc_start_line = i +1
            if '</TEXT>' in data[i]:
                self.doc_finish_line = i
                break

        data[i] = data[i].replace('[Text]', '')
        data[i] = data[i].replace('<TEXT>', '')
        self.text = data[self.doc_start_line:self.doc_finish_line]
        self.doc_pipeline()
        q.put(self) # Inserting the document object so the listener will get it

    def doc_pipeline(self):
        regex = Parse()        # TODO: Need to give parser the stop_words list
        self.tokens = regex.regex_pipeline(self.text, self.stem)
        if self.write_to_disk: # TODO: Not sure it works in python need to check that
            self.to_json() # TODO: Change it to HDF5

    def to_json(self):
        dict_to_json = {}
        dict_to_json['doc_num'] = self.doc_num
        dict_to_json['HT'] = self.HT
        dict_to_json['Text'] = self.text
        dict_to_json['Tokens'] = self.tokens
        # dict_to_json['orig_data'] = data
        with open('C:\\Users\\Nitzan\\Desktop\\AFTER PARSE 1 file\\' + self.doc_num + '.txt', 'w') as outfile:
            json.dump(dict_to_json, outfile)

    def set_text(self, data): # No usage
        start = -1
        finish = -1
        for i in range(0, len(data)):
            if (start == -1 and '<TEXT>' in data[i]) or ('[Text]' in data[i]):
                start = i + 1
            if '</TEXT>' in data[i]:
                finish = i
                break
            if '<F P=104>' in data[i]:
                self.city = data[i].split()[2].upper()
            if '<F P=101>' in data[i]:
                self.topic = data[i].split()[2].upper()
        data[i] = data[i].replace('[Text]', '')
        data[i] = data[i].replace('<TEXT>', '')
        self.text = data[start:finish]

    def get_doc_parameter(self, line, label):
        start_label = '<' + label + '>'
        start_index = line.find('<' + label + '>')
        end_index = line.find('</' + label + '>')
        return line[start_index + len(start_label):end_index].rstrip().lstrip()

if __name__ == '__main__':
    # Debug configs:
    single_file = True
    write_to_disk = True
    parallel = True
    stem = False
    Index = False

    if Index:
        indexer = Indexer()
    start_time = datetime.datetime.now()

    # Single file debug config
    if single_file:
        file = ReadFile(r'C:\Users\Nitzan\Desktop\FB396001', parallel, stem, write_to_disk)
        file.read_directory(r'C:\Users\Nitzan\Desktop\FB396001')
    else:
        # All files debug config
        file = ReadFile(r'C:\Users\Nitzan\Desktop\100 file corpus', parallel, stem, write_to_disk)
        file.run_file_reader()

    finish_time = datetime.datetime.now()
    print(finish_time - start_time)
    # Counter([stemmer.stem(word) for word in word_tokenize(data)]) - This is the stem and tokenizing test, keep this here plz