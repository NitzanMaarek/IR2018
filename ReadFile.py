from Document import Document

class ReadFile:
    def __init__(self, file_name, q, file_path, stop_words_list, stem, save_tokens = False):
        self.file_name = file_name
        self.q = q
        self.file_path = file_path
        self.stem = stem
        self.save_tokens = save_tokens
        self.doc_count = self.read_file(stop_words_list, q) #this should be here

    def read_file(self, stop_words_list, q):
        doc_count = 0
        file = open(self.file_path, 'r', errors='ignore')
        lines = file.readlines()
        for i, line in enumerate(lines, start=0):
            if "<DOC>" in line:
                start = i
            elif "</DOC>" in line:
                doc_count += 1
                doc = Document(data=lines[start + 1: i - 1], file_name=self.file_name,
                               stop_words_list=stop_words_list, first_row_index=start,
                               last_row_index=i-1, stem=self.stem, save_tokens=self.save_tokens)
                q.put(doc)  # Inserting the document object so the listener will get it
        file.close()
        return doc_count