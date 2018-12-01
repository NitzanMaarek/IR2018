from Document import Document

class ReadFile:
    def __init__(self, file_name, stem, write_to_disk, q, file_path, stop_words_list):
        self.file_name = file_name
        self.stem = stem
        self.write_to_disk = write_to_disk
        self.q = q
        self.file_path = file_path
        self.doc_count = self.read_file(stop_words_list) #this should be here

    def read_file(self, stop_words_list):
        doc_count = 0
        # try:
        file = open(self.file_path, 'r', errors='ignore')
        lines = file.readlines()
        for i, line in enumerate(lines, start=0):
            if "<DOC>" in line:
                start = i
            elif "</DOC>" in line:
                doc_count += 1
                Document(data=lines[start + 1: i - 1], file_name=self.file_name , q=self.q, stem=self.stem, write_to_disk=self.write_to_disk, stop_words_list=stop_words_list, first_row_index=start, last_row_index=i-1)
        file.close()
        # except Exception as e:
        #     print(e)
        #     print("Processing file not succeeded: " + self.file_path)
        return doc_count