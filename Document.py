from Parse import Parse
import json

class Document:
    def __init__(self, data, stem, q, write_to_disk):
        self.stem = stem
        self.doc_num = self.get_doc_parameter(data[0], 'DOCNO')
        self.HT = self.get_doc_parameter(data[1], 'HT')
        self.write_to_disk = write_to_disk

        start = -1
        for i in range(0, len(data)):
            if 'DATE1' in data[i]:
                self.date = self.get_doc_parameter(data[i], 'DATE1')
                continue
            if '<F P=104>' in data[i]:
                self.city = data[i].split()[2].upper()
                continue
            if '<F P=101>' in data[i]:
                self.topic = data[i].split()[2].upper()
                continue
            if (start == -1 and '<TEXT>' in data[i]) or ('[Text]' in data[i]):
                self.doc_start_line = i +1
                continue
            if '</TEXT>' in data[i]:
                self.doc_finish_line = i
                break


        data[i] = data[i].replace('[Text]', '')
        data[i] = data[i].replace('<TEXT>', '')
        self.text = data[self.doc_start_line:self.doc_finish_line]
        self.doc_pipeline()
        print(self.doc_num)
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
        with open('C:\\Chen\\BGU\\2019\\2018 - Semester A\\3. Information Retrival\\Engine\\jsons\\' + self.doc_num + '.txt', 'w') as outfile:
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