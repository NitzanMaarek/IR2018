from Parser import Parser
import json
import Preferences
import operator

class Document:
    def __init__(self, file_name = None, data = None, stop_words_list = None,
                 first_row_index = None, last_row_index = None, disk_string = None, stem=False):
        """
        Creating a document object which contains the following parameters
        :param file_name: the file name which the document is from
        :param stem: boolean parameter that indicates if we use stem or not
        :param stop_words_list: stop words list for the parser
        :param first_row_index: the row number that the document is starting in it's document
        :param last_row_index: the row number in which the document ends in
        :param disk_string: string if we want to load the document from a string which was written in the disk
        """
        if not disk_string is None:
            self._define_params_from_string(disk_string)
        else:
            self.file_name = file_name
            self.stem = Preferences.stem
            self.doc_num = self.get_doc_parameter(data[0], 'DOCNO')
            self.HT = self.get_doc_parameter(data[1], 'HT')
            self.doc_start_line = -1
            self.doc_finish_line = -1
            self.stem = stem
            self.dominant_entities_list = {}
            # TODO: create a function out of this
            start = -1
            for i in range(0, len(data)):
                if 'DATE1' in data[i]:
                    self.date = self.get_doc_parameter(data[i], 'DATE1')
                    continue
                if '<F P=101>' in data[i]:
                    after_split = data[i].split()
                    if len(after_split) > 2:
                        self.topic = after_split[2].upper()
                    continue
                if '<F P=104>' in data[i]:
                    after_split = data[i].split()
                    if len(after_split) > 2:
                        self.city = after_split[2].upper()
                        if self.city == 'ST.' or self.city == 'ST':
                            self.city = ''.join([self.city, after_split[3].upper()])
                    continue
                if '<F P=105>' in data[i]:
                    self.language = self.get_doc_parameter(data[i], 'F P=105').split()[0]
                    continue
                # Title section:
                if '<H3>' in data[i]:
                    title = data[i].replace('<H3>', '')
                    title = title.replace('</H3>', '')
                    title = title.replace('<TI>', '')
                    title = title.replace('</TI>', '')
                    self.title = title
                    continue
                if '<HEADLINE>' in data[i]:
                    if 'LA' in self.doc_num:
                        self.title = data[i + 2]
                        continue
                    else:
                        title = data[i + 1][data[i + 1].find('/') + 1:]
                        self.title = title
                        continue
                if (start == -1 and '<TEXT>' in data[i]) or ('[Text]' in data[i]):
                    self.doc_start_line = i +1
                    continue
                if '</TEXT>' in data[i]:
                    self.doc_finish_line = i
                    break

            data[i] = data[i].replace('[Text]', '')
            data[i] = data[i].replace('<TEXT>', '')
            if self.doc_start_line == -1 and self.doc_finish_line == -1:
                self.doc_start_line = first_row_index
                self.doc_finish_line = last_row_index
            else:
                self.doc_pipeline(stop_words_list, data[self.doc_start_line:self.doc_finish_line])

    def doc_pipeline(self, stop_words_list, text):
        """
        Set of actions we want to get the document and it's data through.
        Includes parsing the text, checking if the tokens from the parsing are in the title
        :param stop_words_list: stop words list for the parser
        :param text: the document text, list of strings, each string is a line in the document
        """
        parser = Parser(stop_words_list)
        self.tokens = parser.parser_pipeline(text, self.stem)
        self.max_tf = parser.get_max_tf()
        # parser.erase_dictionary()
        upper_case_appearence_dictionary = parser.get_entities()
        if hasattr(self, 'title'):
            title_parser = Parser(stop_words_list)
            title_tokens = title_parser.parser_pipeline([self.title], self.stem)
            for token in self.tokens:
                if token in title_tokens:
                    self.tokens[token][2] = True
                else:
                    self.tokens[token][2] = False
            self.calculate_dominant_entities(upper_case_appearence_dictionary, title_tokens)
        else:
            self.calculate_dominant_entities(upper_case_appearence_dictionary, None)

    def to_json(self):
        """
        Writes the document and it's parameter to json - WE DON'T USE IT ANYMORE
        """
        dict_to_json = {}
        dict_to_json['doc_num'] = self.doc_num
        dict_to_json['HT'] = self.HT
        dict_to_json['Tokens'] = self.tokens
        # TODO: Is this good?
        with open('C:\\Chen\\BGU\\2019\\2018 - Semester A\\3. Information Retrival\\Engine\\jsons\\' + self.doc_num + '.txt', 'w') as outfile:
            json.dump(dict_to_json, outfile)

    def get_doc_parameter(self, line, label):
        """
        Finds a parameter in a given line by the given tag
        :param line: string - text of the line we want to extract the parameter from.
        :param label: string - label we want to remove from the line string
        :return: the tag as a string
        """
        start_label = '<' + label + '>'
        start_index = line.find('<' + label + '>')
        end_index = line.find('</' + label + '>')
        return line[start_index + len(start_label):end_index].rstrip().lstrip()

    def write_to_disk_string(self):
        """
        NOT BEING USED - creates a string of all the parameters of the document so we can
        create from the string a document object
        :return: parameter string
        """
        params = []
        params.append(str(self.doc_num))
        params.append(str(self.file_name))
        params.append(str(self.doc_start_line))
        params.append(str(self.doc_finish_line))
        if hasattr(self, 'tokens'):
            params.append(str(len(self.tokens)))
        if hasattr(self, 'max_tf'):
            params.append(str(self.max_tf))
        if hasattr(self, 'city'):
            params.append(str(self.city))
        if hasattr(self, 'language'):
            params.append(str(self.language))
        # params.append(str(self.title)) # TODO: need to choose if to return the tokens of the title

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
        if hasattr(self, 'city'):
            self.city = params_list[5]
        if hasattr(self, 'title'):
            self.title = params_list[6]
        if hasattr(self, 'language'):
            self.language = params_list[7]

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

    def calculate_dominant_entities(self, upper_case_appearance_dictionary, parsed_title):
        """
        Method calculates top 5 dominant entities according to the next parameters:
        1. Number of appearances in document.
        2. Entity in title or not.
        3. Position of entity according to total number of tokens in document.
        :param upper_case_appearance_dictionary: List of all upper case words in document
        :param parsed_title: Dictionary of title parsed
        :return: Maximum 5 most dominant entities.
        """
        number_of_lines = self.doc_finish_line-self.doc_start_line
        if len(upper_case_appearance_dictionary) >= 1:
            for entity in upper_case_appearance_dictionary:
                if entity in self.tokens:
                    current_score = self.tokens[entity][0]/self.max_tf          # adding occurrences/max_tf
                    current_score += 1 - self.tokens[entity][1][0]/number_of_lines  # adding 1 - line_position/total_lines.
                    # Means the earlier the entity shows up in doc the better it is (thats why 1-)
                    if parsed_title is not None:
                        if entity in parsed_title:
                            current_score = current_score*2                     # Entity in title gets score*2
                    upper_case_appearance_dictionary[entity] = current_score    # Updating score for each entity
            self.sort_dominant_entities(upper_case_appearance_dictionary)

    def sort_dominant_entities(self, upper_case_appearance_dictionary):
        """
        Method sorts top 5 entities by given score in given dictionary
        Updates document dominant entity list
        :param upper_case_appearance_dictionary: Key = Entity, Value = Score
        """
        sorted_entities = sorted(upper_case_appearance_dictionary.items(), key=operator.itemgetter(1))
        counter = 0
        i = len(sorted_entities) - 1
        while i >= 0:
            if counter >= 5:
                return
            self.dominant_entities_list[sorted_entities[i][0]] = round(sorted_entities[i][1], 2)
            counter += 1
            i -= 1
