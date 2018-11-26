import os
from Parse import Parse
from Document import Document

class ReadFile:
    def __init__(self, stem, write_to_disk, q, file_path):
        self.stem = stem
        self.write_to_disk = write_to_disk
        self.q = q
        self.file_path = file_path
        self.read_file()

    def run_file_reader(self):
        self.read_directory(self.directory)

    # TODO: delete it after making sure the new code is working
    def read_directory(self, directory):
        jobs = []

        for root, dirs, files in os.walk(directory):
            # TODO: Read also stop_words.txt from this directory and forward list to parser init
            Parse.static_stop_words_list = self.read_stop_words_lines(directory)
            for file in files:
                path = os.path.join(root, file)
                if self.multiprocess:
                    job = self.pool.apply_async(self.read_file, (path))
                    jobs.append(job)
                else:
                    self.read_file(path)

        for job in jobs:
            res = job.get()

        self.q.put('kill')

    # TODO: maybe move it to another class? parse probably
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

    def read_file(self):
        try:
            file = open(self.file_path, 'r')
            lines = file.readlines()
            for i, line in enumerate(lines, start=0):
                if "<DOC>" in line:
                    start = i
                elif "</DOC>" in line:
                    Document(data=lines[start + 1: i - 1], q=self.q, stem=self.stem, write_to_disk=self.write_to_disk)
            file.close()
        except Exception as e:
            print(e)
            print("Processing file not succeeded: " + self.file_path)
        return self.file_path