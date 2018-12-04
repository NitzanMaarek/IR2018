from Parser import Parser
import json
import Preferences


class Document:
    def __init__(self, file_name = None, data = None, stem = False, write_to_disk = False, stop_words_list = None,
                 first_row_index = None, last_row_index = None, disk_string = None):
        if not disk_string is None:
            self._define_params_from_string(disk_string)
        else:
            self.file_name = file_name
            self.stem = stem
            self.doc_num = self.get_doc_parameter(data[0], 'DOCNO')
            self.HT = self.get_doc_parameter(data[1], 'HT')
            self.write_to_disk = write_to_disk
            self.doc_start_line = -1
            self.doc_finish_line = -1
            # TODO: create a function out of this
            start = -1
            for i in range(0, len(data)):
                if 'DATE1' in data[i]:
                    self.date = self.get_doc_parameter(data[i], 'DATE1')
                    continue
                if '<F P=104>' in data[i]:
                    after_split = data[i].split()
                    if len(after_split) > 2:
                        # self.city = after_split[2].upper()
                        self.city = after_split[2].upper()
                        # cities_index.get_city_attributes(self.city, self.doc_num)
                    continue
                if '<F P=101>' in data[i]:
                    after_split = data[i].split()
                    if len(after_split) > 2:
                        self.topic = after_split[2].upper()
                    continue
                # Title section:
                # TODO: remove self.title_str if not needed in the end
                if '<H3>' in data[i]:
                    title = data[i].replace('<H3>', '')
                    title = title.replace('</H3>', '')
                    title = title.replace('<TI>', '')
                    title = title.replace('</TI>', '')
                    self.title_str = title
                    self.title = title.split()
                    continue
                if '<HEADLINE>' in data[i]:
                    if 'LA' in self.doc_num:
                        self.title_str = data[i + 2]
                        self.title = data[i + 2].split()
                        continue
                    else:
                        title = data[i + 1][data[i + 1].find('/') + 1:]
                        self.title_str = title
                        self.title = title.split()
                        continue
                if (start == -1 and '<TEXT>' in data[i]) or ('[Text]' in data[i]):
                    self.doc_start_line = i +1
                    continue
                if '</TEXT>' in data[i]:
                    self.doc_finish_line = i
                    break

            # print(self.doc_num + ': ' + self.title_str)
            data[i] = data[i].replace('[Text]', '')
            data[i] = data[i].replace('<TEXT>', '')
            if self.doc_start_line == -1 and self.doc_finish_line == -1:
                self.doc_start_line = first_row_index
                self.doc_finish_line = last_row_index
            else:
                # self.text = data[self.doc_start_line:self.doc_finish_line]
                self.doc_pipeline(stop_words_list, data[self.doc_start_line:self.doc_finish_line])
            # print(self.doc_num)
            # q.put(self) # Inserting the document object so the listener will get it

    def doc_pipeline(self, stop_words_list, text):
        parser = Parser(stop_words_list)        # TODO: Need to give parser the stop_words list
        self.tokens = parser.parser_pipeline(text, self.stem)
        self.max_tf = parser.get_max_tf()

    def to_json(self):
        dict_to_json = {}
        dict_to_json['doc_num'] = self.doc_num
        dict_to_json['HT'] = self.HT
        # dict_to_json['Text'] = self.text
        dict_to_json['Tokens'] = self.tokens
        # dict_to_json['orig_data'] = data
        with open('C:\\Chen\\BGU\\2019\\2018 - Semester A\\3. Information Retrival\\Engine\\jsons\\' + self.doc_num + '.txt', 'w') as outfile:
            json.dump(dict_to_json, outfile)

    def get_doc_parameter(self, line, label):
        start_label = '<' + label + '>'
        start_index = line.find('<' + label + '>')
        end_index = line.find('</' + label + '>')
        return line[start_index + len(start_label):end_index].rstrip().lstrip()

    def write_to_disk_string(self):
        params = []
        params.append(str(self.doc_num))
        params.append(str(self.file_name))
        params.append(str(self.doc_start_line))
        params.append(str(self.doc_finish_line))
        if hasattr(self, 'max_tf'):
            params.append(str(self.max_tf))
        if hasattr(self, 'city'):
            params.append(str(self.city))
        # params.append(str(self.title_str)) # TODO: need to choose if to return the tokens of the title

        return ' '.join(params)

    def _define_params_from_string(self, params_string):
        """
        Used for initiating an document object using string from posting file which is written in the disk
        :param params_string: string which represents the parameters of the object
        """
        params_list = params_string.split()
        self.doc_num = params_list[0]
        self.file_name = params_list[1]
        self.doc_start_line = int(params_list[2])
        self.doc_finish_line = int(params_list[3])
        self.max_tf = params_list[4]
        self.city = params_list[5]
        self.title_str = params_list[6]

    def set_pointer(self, batch_num, seek_value):
        """
        Adds value of the pointer to the document posting
        :param batch_num: the batch number which represents the posting file code
        :param seek_value:
        :return:
        """
        self.batch_num = batch_num
        self.seek_value = seek_value

    def get_pointer_as_string(self):
        """
        Function to get the document pointer
        :return: string which represents the pointer
        """
        string_list = [str(self.batch_num), self.file_name[:2], str(self.seek_value)]
        return ' '.join(string_list)