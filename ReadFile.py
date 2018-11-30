import os
from Parse import Parse
from Document import Document

class ReadFile:
    def __init__(self, stem, write_to_disk, q, file_path, stop_words_list):
        self.stem = stem
        self.write_to_disk = write_to_disk
        self.q = q
        self.file_path = file_path
        self.read_file(stop_words_list) #this should be here

    def read_file(self, stop_words_list):
        try:
            file = open(self.file_path, 'r', errors='ignore')
            lines = file.readlines()
            for i, line in enumerate(lines, start=0):
                if "<DOC>" in line:
                    start = i
                elif "</DOC>" in line:
                    Document(data=lines[start + 1: i - 1], q=self.q, stem=self.stem, write_to_disk=self.write_to_disk, stop_words_list=stop_words_list)
            file.close()
        except Exception as e:
            print(e)
            print("Processing file not succeeded: " + self.file_path)
        return self.file_path