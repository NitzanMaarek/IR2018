from nltk.stem.porter import *
import Preferences

class Parser:
    """

    """
    def __init__(self, stop_words_list, stem=None):
        """

        :param stop_words_list:
        """

        if not stem is None:
            self.stem = stem

        self.percent_key_words = {'%', 'percent', 'percentage'}
        self.dollar_key_words = {'$', 'Dollars', 'dollars'}
        self.month_dictionary = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
                                 'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12',
                                 'JANUARY': '01', 'FEBRUARY': '02', 'MARCH': '03', 'APRIL': '04', 'MAY': '05', 'JUNE': '06', 'JULY': '07',
                                 'AUGUST': '08', 'SEPTEMBER': '09', 'OCTOBER': '10', 'NOVEMBER': '11', 'DECEMBER': '12',
                                 'january': '01', 'february': '02', 'march': '03', 'april': '04', 'may': '05', 'june': '06',
                                 'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11', 'december': '12',
                                 'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'JUN': '06', 'JUL': '07', 'AUG': '08',
                                 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12', 'Jan': '01', 'Feb': '02', 'Mar': '03',
                                 'Apr': '04', 'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11',
                                 'Dec': '12', 'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'jun': '06', 'jul': '07',
                                 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'}
        self.data_byte_dictionary = {'bit': 'b', 'BIT': 'b', 'Bit': 'b', 'byte': 'B', 'BYTE': 'B', 'Byte': 'B',
                                     'kilobyte': 'KB', 'KILOBYTE': 'KB', 'Kilobyte': 'KB', 'megabyte': 'MB',
                                     'MEGABYTE': 'MB', 'Megabyte': 'MB', 'terabyte': 'tb', 'gigabyte': 'GB',
                                     'Gigabyte': 'GB', 'GIGABYTE': 'GB','TERABYTE': 'TB', 'Terabyte': 'TB',
                                     'kilo-byte': 'KB', 'Kilo-Byte': 'KB', 'KILO-BYTE': 'KB',
                                     'mega-byte': 'MB', 'Mega-Byte': 'MB', 'MEGA-BYTE': 'MB', 'giga-byte': 'GB',
                                     'Giga-Byte': 'GB', 'GIGA-BYTE': 'GB','tera-byte': 'TB', 'Tera-Byte': 'TB',
                                     'TERA-BYTE': 'TB', 'bits': 'b', 'BITS': 'b', 'Bits': 'b', 'bytes': 'B',
                                     'BYTES': 'B', 'Bytes': 'B', 'kilobytes': 'KB', 'KILOBYTES': 'KB', 'Kilobytes': 'KB',
                                     'megabytes': 'MB', 'MEGABYTES': 'MB', 'Megabytes': 'MB', 'terabytes': 'tb', 'TERABYTES': 'TB',
                                     'Terabytes': 'TB', 'kilo-bytes': 'KB', 'Kilo-Bytes': 'KB', 'KILO-BYTES': 'KB',
                                     'mega-bytes': 'MB', 'Mega-Bytes': 'MB', 'MEGA-BYTES': 'MB', 'tera-bytes': 'TB',
                                     'Tera-Bytes': 'TB', 'TERA-BYTES': 'TB', 'kilobit': 'kb', 'kilo-bit': 'kb', 'KILOBIT': 'kb',
                                     'Kilobit': 'kb', 'kilobits': 'kb', 'kilo-bits': 'kb', 'KILOBITS': 'kb',
                                     'Kilobits': 'kb', 'megabit': 'mb', 'megabits': 'mb', 'MEGABIT': 'mb', 'MEGABITS': 'mb',
                                     'mega-bit': 'mb', 'mega-bits': 'mb', 'gigabit': 'gb', 'gigabits': 'gb', 'GIGABIT': 'gb',
                                     'GIGABITS': 'gb', 'giga-bit': 'gb', 'giga-bits': 'gb', 'terabit': 'tb', 'terabits': 'tb',
                                     'tera-bit': 'tb', 'tera-bits': 'tb'}

        # locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        self.sides_delimiters = {' ', ',', '.', '/', '"', '\'', '\\', '(', ')', '[', ']', '{', '}', ':', '-', ';', '?', '!', '*', '>', '<', '&', '+', '#', '@', '^', '_', '=', '`', '|'}
        self.beginning_delimiters = {'%',' ', ',', '.', '/', '"', '\'', '\\', '(', ')', '[', ']', '{', '}', ':', '-', ';', '?', '!', '*', '>', '<', '&', '+', '#', '@', '^', '_', '=', '`', '|'}
        self.end_delimiters = {'$', ' ', ',', '.', '/', '"', '\'', '\\', '(', ')', '[', ']', '{', '}', ':', '-', ';', '?', '!', '*', '>', '<', '&', '+', '#', '@', '^', '_', '=', '`', '|'}
        self.middle_delimiters = {' ', ',', '.', '/', '"', '\\', '(', ')', '[', ']', '{', '}', ':', '-', ';', '?', '!', '*', '>', '<', '&', '+', '#', '@', '^', '_', '=', '`', '|'}
        self.token_index = 0
        self.word = ''
        self.line_index = 0     # Index of words in a line
        self.line = ''
        self.data_index = 0     # Index of lines in data
        self.data = None
        self.skip_tokenize = 0  # Indicates how many tokens to skip to not tokenize
        self.stop_words_list = stop_words_list
        self.token_dictionary_num_of_appearance = {}        # Contains final tokens with number of appearences
        self.token_dictionary_first_position = {}           # Contains final tokens with first position appeared
        self.token_upper_case_dictionary = {}               # Contains all upper case words parsed AFTER filtering with lower case.
                                                            # Key = Term upper case, Value = number of appearences.
        self.max_tf = 0


    def parser_pipeline(self, data, stem):
        """
        Main method of this class. In charge of the initializing the parsing and tokenizing process.
        :param data: string of data you want to parse and tokenize
        :param stem: boolean flag, True = use stemming, False otherwise.
        :return: Dictionary of tokens as keys and its' attributes as values.
        """
        self.data = data
        self.stem = stem
        tokens = self.create_tokens(self.data)
        # tokens = self.find_key_words_in_line(tokens)
        return tokens

    def erase_dictionary(self):
        """
        Method erases collections
        """
        self.token_dictionary_first_position.clear()
        self.token_dictionary_num_of_appearance.clear()
        self.token_upper_case_dictionary.clear()
        self.tokens = []

    def create_tokens(self, data):
        """
        Method iterates over data, parses it and tokenizes it.
        :param data: String of data to parse and tokenize.
        :return: Dictionary of tokens as keys and its' frequency and first position in doc
        """
        self.tokens = []
        self.data_length = len(data)
        stop_words_length = len(self.stop_words_list)
        self.between_index = 0
        for data_index, line in enumerate(data, start=0):
            self.data_index = data_index
            self.line = line.split()
            for line_index, word in enumerate(self.line, start=0):
                if self.skip_tokenize > 0:
                    self.skip_tokenize -= 1
                    continue
                self.line_index = line_index
                self.word = word

                # if Preferences.ignore_tag_p:
                if self.word == '<P>' or self.word == '</P>':
                    continue

                self.word = self.remove_delimiters(self.word)
                if self.word is None:
                    continue

                if self.word == 'between' or self.word == 'Between':
                    self.between_index = 1
                word = self.turn_all_to_lower_case(word)
                if self.between_index == 0 and (stop_words_length != 0 and word in self.stop_words_list):
                    continue

                # Here we're supposed to have the word (not stop-word) without any delimiters
                # Word is normal word and also String with delimiters in inside: number with comma, words with slash etc..
                token = self.parse_strings()

                if token is not None and len(token) > 0:
                    if self.between_index >= 1:
                        token = self.parse_handle_between_token(token)   # If we've encountered the word between then keep track if next tokens are : between <number> and <number>
                if token is not None and len(token) > 0:
                    self.add_token_to_collections(token, (data_index, line_index))

        self.correct_upper_lower_cases()
        return self.merge_dictionaries()

        # return self.tokens

    def correct_upper_lower_cases(self):
        """
        Checks every upper case word written if it was written in lower case -> transform to lower case
        """
        upper_case_tokens_to_delete_list = []
        if len(self.token_upper_case_dictionary) > 0:
            for upper_case_token in self.token_upper_case_dictionary:             #For each capital letter word
                lower_case_token = self.turn_all_to_lower_case(upper_case_token)
                if lower_case_token in self.token_dictionary_num_of_appearance and upper_case_token in self.token_dictionary_num_of_appearance:         #If also lower case exists
                    #Merge upper and lower cases into lower case
                    upper_position = self.token_dictionary_first_position[upper_case_token]
                    upper_frequencey = self.token_dictionary_num_of_appearance[upper_case_token]
                    lower_position = self.token_dictionary_first_position[lower_case_token]
                    upper_line_pos = upper_position[0]
                    lower_line_pos = lower_position[0]
                    if upper_line_pos < lower_line_pos:     # Sort according to first position.
                        self.token_dictionary_first_position[lower_case_token] = upper_position
                    elif upper_line_pos > lower_line_pos:
                        self.token_dictionary_first_position[lower_case_token] = lower_position
                    else:
                        upper_word_pos = upper_position[1]
                        lower_word_pos = lower_position[1]
                        if upper_word_pos < lower_word_pos:
                            self.token_dictionary_first_position[lower_case_token] = upper_position
                        else:
                            self.token_dictionary_first_position[lower_case_token] = lower_position
                    self.token_dictionary_num_of_appearance[lower_case_token] += upper_frequencey
                    del self.token_dictionary_num_of_appearance[upper_case_token]
                    del self.token_dictionary_first_position[upper_case_token]
                    upper_case_tokens_to_delete_list.append(upper_case_token)

        # Removing all upper case tokens that also appeared in lower case
        for token in upper_case_tokens_to_delete_list:
            del self.token_upper_case_dictionary[token]

    def merge_dictionaries(self):
        """
        Method merges dictionaries of token first_position and frequency.
        Also calculates maximum term frequency when iterating dictionaries during merge.
        We add another boolean value which will represents if the token appears in the title or not, it is initialized
        to False and will be changed in the future according to the document title.
        :return: one merged dictionary.
        """
        if self.token_dictionary_first_position.__sizeof__() > 1:
            max_tf_count = 0
            max_tf_token = ''
            merged_sorted_dictionary = {}
            for (key_p, value_p), (key_f, value_f) in zip(self.token_dictionary_first_position.items(), self.token_dictionary_num_of_appearance.items()):
                # key_p, value_p = items in dictionary of first Position
                # key_f, value_f = items in dictionary of Frequency/appearances
                if key_f != max_tf_token:
                    if value_f > max_tf_count:
                        max_tf_token = key_f
                        max_tf_count = value_f

                merged_sorted_dictionary[key_p] = [self.token_dictionary_num_of_appearance[key_f], self.token_dictionary_first_position[key_p], False]

            self.max_tf = max_tf_count

            for stop_word in self.stop_words_list:
                if stop_word in merged_sorted_dictionary:
                    del merged_sorted_dictionary[stop_word]

            return merged_sorted_dictionary
        return None

    def get_max_tf(self):
        """
        Method returns the maximum term frequency in the given data
        :return: maximum term frequency in data
        """
        return self.max_tf

    def add_token_to_collections(self, token, position_list):
        """
        Method adds/updates token to dictionaries
        :param token: one token or list of tokens to add or update and list = (line_number, position_in_line)
        :param position_list: list of position in doc (lines) and position in line (words)
        """
        if self.stem:
            stemmer = PorterStemmer()

        if type(token) is list:
            for item in token:
                if self.stem and not self.is_any_kind_of_number(item):
                    item = stemmer.stem(item)
                if self.token_dictionary_first_position.__contains__(item):
                    self.token_dictionary_num_of_appearance[item] += 1
                else:
                    self.token_dictionary_num_of_appearance[item] = 1
                    self.token_dictionary_first_position[item] = position_list
                self.tokens.append(item)
        else:
            if self.stem and not self.is_any_kind_of_number(token):
                token = stemmer.stem(token)
            if self.token_dictionary_first_position.__contains__(token):
                self.token_dictionary_num_of_appearance[token] += 1
            else:
                self.token_dictionary_num_of_appearance[token] = 1
                self.token_dictionary_first_position[token] = position_list
            self.tokens.append(token)

    def remove_delimiters(self, word):
        """
        Method receives string and removes all delimiters in beginning and end of string
        :param word: string parsed by split()
        :return: word without delimiters in both ends, None if all word was delimiters
        """
        last = len(word) - 1
        first = 0
        while first <= last and (word[last] in self.end_delimiters or word[first] in self.beginning_delimiters):  # loop to remove delimiters
            if word[first] in self.beginning_delimiters:
                first += 1
            if word[last] in self.end_delimiters:
                last -= 1
        if first > last:  # Means all word was delimiters and need to ignore it.
            return None
        else:  # Means not all of the word is delimiters
            word = word[first:last + 1]
        return word

    def delete_token_i(self, i):
        """
        Method deletes token i (from end of list) from both tokens list and tokens dictionary
        in the dictionary it decreases number of appearances by 1, if last appearance then delete from dictionary
        :param i: number of tokens from end of list to delete
        """
        token_to_operate = self.tokens[-i]
        token_frequency = self.token_dictionary_num_of_appearance.get(token_to_operate, 0)
        if token_frequency > 1:
            self.token_dictionary_num_of_appearance[token_to_operate] -= 1
        elif token_frequency == 1:
            del self.token_dictionary_num_of_appearance[token_to_operate]
            del self.token_dictionary_first_position[token_to_operate]
        del self.tokens[-i]

    def parse_handle_between_token(self, parsed_token):
        """
        If we've encountered the word between then keep track if next tokens are : between <number> and <number>
        between index 1 is 'between', 2 is the first number, 3 is 'and', and 4is the last number
        :param parsed_token: token after parse
        :return: token 'between <number> and <number>' after deletion if sequence complete, normal token otherwise
        """
        token = parsed_token
        if type(token) != str:
            self.between_index = 0
            # if 'between' in self.stop_words_list or 'Between' in self.stop_words_list:
            #     self.delete_token_i(1)
            return token
        if self.between_index == 2:
            if self.is_any_kind_of_number(token):       # If second string is number
                self.between_index += 1
            else:
                self.between_index = 0
                # if 'between' in self.stop_words_list or 'Between' in self.stop_words_list:
                #     self.delete_token_i(1)
                if token in self.stop_words_list:
                    return None

        elif self.between_index == 3:
            if token == 'and':
                self.between_index += 1
            else:
                self.between_index = 0
                # if 'between' in self.stop_words_list or 'Between' in self.stop_words_list:
                #     try:
                #         self.delete_token_i(2)      # Delete the word between
                #     except Exception as e:
                #         print('nizo')
                if token in self.stop_words_list:
                    return None

        elif self.between_index == 4:
            if self.is_any_kind_of_number(token):
                self.between_index = 0
                token_list = ['between ' + self.tokens[-2] + ' and ' + token, token]
                self.delete_token_i(3)  # delete the token 'between'
                self.delete_token_i(1)  # delete the token 'and'
                return token_list
            else:
                self.between_index = 0
                if token in self.stop_words_list:
                    return None
                # if 'between' in self.stop_words_list or 'Between' in self.stop_words_list:
                #     self.delete_token_i(3)  # delete the token 'between'
                # if 'and' in self.stop_words_list:
                #     self.delete_token_i(1)  # delete the token 'and'
        else:
            self.between_index += 1
        return token

    def get_next_word(self):
        """
        Method iterates over data if next word exists and returns it
        :return: next word in data, None if end of text.
        """
        if len(self.line) == self.line_index + 1:                   #If current word is last in line
            if self.data_length > self.data_index + 1:                #If current line is NOT last line
                next_line = self.get_next_line()
                if next_line is None:
                    return None
                first_word_next_line = next_line.split()[0]
                if first_word_next_line is not None:
                    last_char_next_word = first_word_next_line[-1]
                    if last_char_next_word in self.sides_delimiters:  # Check if next word contains delimiter as last char.
                        first_word_next_line = first_word_next_line[:-1]
                return first_word_next_line          #Take next word in next line in case its important
        else:
            next_word = self.line[self.line_index + 1]
            if next_word is not None:
                last_char_next_word = next_word[-1]
                if last_char_next_word in self.sides_delimiters:  # Check if next word contains delimiter as last char.
                    next_word = next_word[:-1]
            return next_word           # Not last in line? return the next word in line then
        return None

    def get_entities(self):
        return self.token_upper_case_dictionary

    def get_word_i(self, i):
        """
        Method iterates over data if and returns item i from where we are if exists
        i = 1 means next word, i = 2 second next word and so on.
        :return: word i in data, None if doesnt exist.
        """
        if len(self.line) == self.line_index + i:                   #If current word is last in line
            if self.data_length > self.data_index + 1:                #If current line is NOT last line
                return self.data[self.data_index + 1].split()[i-1]          #Take next word in next line in case its important
        else:
            return self.line[self.line_index + i]           # Not last in line? return the next word in line then
        return None

    def get_next_line(self):
        """
        Assumption that there is a next line:
        Method will iterate over empty lines until it reaches a line which is not empty
        :return: not empty line, None if there is no empty line after (end of file)
        """
        index_of_lines = self.data_index
        data_length = self.data_length
        while data_length > index_of_lines + 1:
            if self.data[index_of_lines + 1] == '\n':
                index_of_lines += 1
            else:
                return self.data[index_of_lines + 1]
        return None

    def parse_strings(self):
        """
        Main parse function - parses according to specific rules.
        :return: final Token after parse according to all rules.
        """
        token = self.word
        if token is None or len(token) == 0:
            return None

        first_token = token[0]
        if first_token == '1' or first_token == '2' or first_token == '3' or first_token == '4' or first_token == '5' or first_token == '6' or first_token == '7' or first_token == '8' or first_token == '9':
            token = self.parse_string_only_number()
        elif first_token == '$':
            token = self.parse_dollar_sign_with_number()
        elif first_token == 'D' and token == 'Dollars':
            token = self.parse_dollar_with_capital_d()
        elif first_token == 'd' and token == 'dollars':
            token = self.parse_dollar_small_d()
        elif token in self.month_dictionary:
            token = self.parse_date_with_month()
        elif (first_token == 'p' or first_token == 'P') and (token == 'percent' or token == 'Percent' or token == 'percentage' or token == 'Percentage'):
            token = self.parse_percent_word()
        elif token in self.data_byte_dictionary:
            token = self.parse_byte_tokens()

        if token is None:
            return None

        first_token = token[0]
        if 'A' <= first_token <= 'Z':
            token = self.upper_case_word(token)
            if token not in self.token_upper_case_dictionary:
                self.token_upper_case_dictionary[token] = 1
            else:
                self.token_upper_case_dictionary[token] += 1
        elif 'a' <= first_token <= 'z':
            token = self.lower_case_word(token)

        return token

    def parse_byte_tokens(self):
        """
        Method handles when a binary "data_type" key word is found: self.data_byte_dictionary
        If token before keyword is a number then delete that token and tokenie key word and number together to one token.
        :return: Token: <number> <data_byte_unit>
        """
        token = self.word
        if len(self.tokens) >= 1:
            previous_number = self.tokens[-1]
            if previous_number.__contains__(','):
                previous_number = previous_number.replace(',', '')
            if self.is_integer(previous_number):
                if previous_number[-1] == 'K':
                    previous_number = self.fix_thousands_for_dollars(previous_number)
                units = self.data_byte_dictionary[token]
                token = ''.join([previous_number, ' ', units])
                self.delete_token_i(1)
        return token

    def turn_all_to_lower_case(self, token):
        """
        Method turns token to lower case
        :param token: string
        :return: lower case token
        """
        ans = []
        for i, char in enumerate(token, start=0):
            char_int_rep = ord(char)
            if 65 <= char_int_rep <= 90:  # if char is UPPER case, make it lower case
                ans.append(chr(char_int_rep + 32))
            else:
                ans.append(char)

        return ''.join(ans)

    def lower_case_word(self, token):
        """
        Method checks if token is an alphabetical word. If so make it lower case
        :param token: string
        :return: if word: then same word in lower case, otherwise same token
        """
        chars_list = []    #list of strings to join after.
        if token is not None:
            hyphen_count = token.count('-')
            if hyphen_count == 1:
                hyphen_position = token.find('-')
                token = self.handle_adjacent_words(token, hyphen_position)
                after_split = token.split('-')
                first_word = after_split[0]
                second_word = after_split[1]
                self.add_token_to_collections(first_word, (self.data_index, self.line_index))
                self.add_token_to_collections(second_word, (self.data_index, self.line_index))
            else:
                for i, char in enumerate(token, start=0):
                    char_int_rep = ord(char)
                    if 65 <= char_int_rep <= 90:     #if char is UPPER case, make it lower case
                        chars_list.append(chr(char_int_rep + 32))
                    else:
                        chars_list.append(char)

                token = ''.join(chars_list)
        return token

    def upper_case_word(self, token):
        """
        Method turns word to uppercase if and only if the entire word contains alphabetical letters.
        :param token: string
        :return: upper-case word if entire word is alphabetical, if not it returns same token.
        """
        chars_list = []  # list of strings to join after
        if token is not None:
            hyphen_count = token.count('-')
            if hyphen_count == 1:
                hyphen_position = token.find('-')
                token = self.handle_adjacent_words(token, hyphen_position)
                after_split = token.split('-')
                first_word = after_split[0]
                second_word = after_split[1]
                self.add_token_to_collections(first_word, (self.data_index, self.line_index))
                self.add_token_to_collections(second_word, (self.data_index, self.line_index))
            else:
                for char in token:
                    char_int_rep = ord(char)
                    if 97 <= char_int_rep <= 122:  # if char is LOWER case, make it upper case
                        chars_list.append(chr(char_int_rep - 32))
                    else:
                        chars_list.append(char)
                token = ''.join(chars_list)
        return token

    def handle_adjacent_words(self, token, hyphen_position):
        """
        Method handles cases when: word-word or word-number
        :param token: string with [a-zA-Z]-<something> when something is any kind of char or string
        :param hyphen_position: position of the hyphen
        :return: token ready to add to collection
        """
        if token is None or hyphen_position <= 0:
            return None
        # print('Handling token: ' + token)
        first_str = token[:hyphen_position]
        second_str = token[hyphen_position+1:]
        parser = Parser([], stem=self.stem)
        parse_me = ''.join([first_str, ' ', second_str])
        parsed_str_dic = parser.create_tokens([parse_me])
        parsed_list = list(parsed_str_dic.keys())
        first_str = parsed_list[0]
        if len(parsed_list) <= 1:
            second_str = parsed_list[0]
        else:
            second_str = parsed_list[1]
        if self.is_any_kind_of_number(second_str):
            self.add_token_to_collections(second_str, (self.data_index, self.line_index))
        return ''.join([first_str, '-', second_str])

    def check_if_day_is_range(self, token):
        """
        Checks if given token is <parsed_number>-<parsed_number> and if so count it as a number
        :param token: some text with '-' in it
        :return: True if <parsed_number>-<parsed_number>. False otherwise
        """
        if token is not None:
            after_split = token.split('-')
            if len(after_split) == 2:
                first_number = after_split[0]
                second_number = after_split[1]
                if self.is_integer(first_number) and self.is_integer(second_number) and (1 <= int(first_number) < int(second_number) <= 31):
                    return True
        return False

    def parse_date_with_month(self):
        """
        Parses the next cases:  1. <day> <month>  or  <month> <day>   ->  <month_number>-<day>
                                2. <month> <year>   ->  <year>-<month_number>
            *** NEW RULE ***    3. <day> <month> <year> or <day> <month>, <year>  -> <year>-<month>-<day> and also cases 1 and 2.
        :return: List of tokens: either length of 1 (cases 1 and 2) or length of 3 (case 3)
                1. length of 1: this method will call other function to skip next/delete previous token (the day/year) and return the new correct token to be appended
                2. length of 3: this method will call parse_day_month_year(date_list) delete previous (day), mark to skip next (year), add 2 tokens and return the thirds to be appended.
        """
        token = self.word
        day = None
        if len(self.tokens) >= 1:
            day = self.tokens[-1]
        if day is not None and ((self.is_integer(day) and 1 <= int(day) <= 31) or (self.check_if_day_is_range(day))):
            # There is a day before, we will check if there is also year
            year = self.get_next_word()
            if year is not None and self.is_integer(year) and 1800 <= int(year) <= 2030:  #accept years between 1800 and 2030
                token = self.parse_day_month_year((day, token, year))
            else:
                # There is only day before and no year after month
                token = self.parse_day_before_month_no_year((day, token))
        else:
            # There is no day before month: Need to check if day or year after month
            next_word = self.get_next_word()
            if next_word is not None:
                if self.is_integer(next_word):
                    next_word_int = int(next_word)
                    if 1 <= next_word_int <= 31:
                        token = self.parse_day_after_month((next_word, token))
                    elif 1800 <= next_word_int <= 2030:
                        token = self.parse_year_after_month((token, next_word))
                elif self.check_if_day_is_range(next_word):
                    token = self.parse_day_after_month((next_word, token))
        return token

    def parse_year_after_month(self, date_list):
        """
        Method marks to skip 1 token and return correct token
        :param date_list: (month, year)
        :return: token = <year>-<month>
        """
        token = date_list[1] + '-' + self.month_dictionary.get(date_list[0])
        self.skip_tokenize = 1
        return token

    def parse_day_after_month(self, date_list):
        """
        Method marks to skip next tokenize and returns correct token
        :param date_list: (day, month)
        :return: token = <month>-<day>
        """
        token = self.month_dictionary.get(date_list[1]) + '-' + self.change_day_format(date_list[0])
        self.skip_tokenize = 1
        return token

    def parse_day_before_month_no_year(self, date_list):
        """
        Method deletes previous (day) and returns <month>-<day>
        :param date_list: (day, month) = no need to check input
        :return: token = <month>-<day>
        """
        token = self.month_dictionary.get(date_list[1]) + '-' + self.change_day_format(date_list[0])
        self.delete_token_i(1)
        # del self.tokens[-1]
        return token

    def parse_day_month_year(self, date_list):
        """
        Method will delete previous (day), mark to skip next (year), add 2 tokens and return the thirds to be appended.
        :param date_list: (day, month, year) = no need to check input
        :return: token: <year>-<month_number>-<day>
        """
        month = self.month_dictionary.get(date_list[1])
        day = self.change_day_format(date_list[0])
        year = date_list[2]
        self.delete_token_i(1)      #Delete tokenized day
        # del self.tokens[-1]
        token = [year + '-' + month + '-' + day, month + '-' + day, year + '-' + month]
        self.skip_tokenize = 1
        return token

    def parse_percent_word(self):
        """
        Method deletes previous token if it is a number and creates one token of the previous number and the sign %.
        :return: token = <number>%
        """
        token = self.word
        if len(self.tokens) >= 1:
            previous_token = self.tokens[-1]
            if self.is_any_kind_of_number(previous_token):
                token = previous_token + '%'
                # *** Here need to delete last token which is the number and return <number>%
                self.delete_token_i(1)
                # del self.tokens[-1]
        return token

    def parse_dollar_with_capital_d(self):
        """
        Method handles situations when:     1. price Dollars
                                            2. price m Dollars
                                            3. price bn Dollars
        :return: if sequence is correct then <number=price> Dollars, otherwise the same token given.
        """
        token = self.word
        if len(self.tokens) >= 1:
            previous_token = self.tokens[-1]
            if (len(previous_token) >= 2 and previous_token[-1] == 'm') or (len(previous_token) >= 3 and previous_token[-2:] == 'bn'):
                if previous_token[-1] == 'm':
                    price = previous_token[:-1]
                    if self.is_integer(price) or self.is_float(price):
                        token = self.parse_dollar_sign_with_parsed_number_million(('$', price + 'M'))
                elif previous_token[-2:] == 'bn':
                    price = previous_token[:-2]
                    if self.is_integer(price) or self.is_float(price):
                        token = self.parse_dollar_sign_with_parsed_number_million(('$', price + 'B'))
                    # *** Here need to delete token <number/price><m/bn> because it was tokenized earlier
                self.delete_token_i(1)
                # del self.tokens[-1]
            elif self.is_any_kind_of_number(previous_token):
                price = str(previous_token)
                if price.__contains__('K'):
                    price = self.fix_thousands_for_dollars(price)
                    token = price + ' Dollars'
                elif price.__contains__('M') or price.__contains__('B') or price.__contains__('T'):
                    token = self.parse_dollar_sign_with_parsed_number_million(('$', previous_token))
                else:
                    token = price + ' Dollars'

                # *** Here need to delete last token which was the number because now adding <number> Dollars
                self.delete_token_i(1)
                # del self.tokens[-1]

        return token

    def fix_thousands_for_dollars(self, price_in_thousands):
        """
        Functions substitutes thousands of currency to correct format for currency
        Also does the same for Bytes and Bits.
        :param price_in_thousands: string of price in thousands: 5.1k or 42k  (with comma or without)
        :return: Instead of a number with K to mark thousand, a  normal number without K.
        """
        k_position = price_in_thousands.find('K')
        if price_in_thousands.__contains__('.'):  # If number is: 3.1K or 4.12K or 5.123K
            dot_position = price_in_thousands.find('.')
            if k_position - dot_position == 2:
                price_in_thousands = price_in_thousands.replace('.', ',')
                price_in_thousands = price_in_thousands.replace('K', '00')
            elif k_position - dot_position == 3:
                price_in_thousands = price_in_thousands.replace('.', ',')
                price_in_thousands = price_in_thousands.replace('K', '0')
            elif k_position - dot_position == 4:
                price_in_thousands = price_in_thousands.replace('.', ',')
                price_in_thousands = price_in_thousands.replace('K', '')
        else:  # If number has no comma
            price_in_thousands = price_in_thousands.replace('K', ',000')
        return price_in_thousands

    def parse_dollar_small_d(self):
        """
        Method handles situations where:    1. price million/billion/trillion U.S dollars
        :return: <number=price> Dollars
        """
        token = self.word
        indicator = False           #indicator if in face we tokenized dollar like in rules and so need to delete previouse tokens.
        if len(self.tokens) >= 3:
            us_token = self.tokens[-1]
            price_scale = self.tokens[-2]
            price = self.tokens[-3]
            if us_token == 'U.S':
                if price_scale == 'million':
                    token = self.parse_dollar_sign_with_parsed_number_million(('$', price + 'M'))
                    indicator = True
                elif price_scale == 'billion':
                    token = self.parse_dollar_sign_with_parsed_number_million(('$', price + 'B'))
                    indicator = True
                elif price_scale == 'trillion':
                    token = self.parse_dollar_sign_with_parsed_number_million(('$', price + 'T'))
                    indicator = True
                if indicator:           #Delete last three tokens: <price> <million/billion/trillin> <U.S> to add new token.
                    self.delete_token_i(3)
                    self.delete_token_i(2)
                    self.delete_token_i(1)
                    # del self.tokens[-3]
                    # del self.tokens[-2]
                    # del self.tokens[-1]
        return token

    def parse_string_only_number(self):
        """
        Method checks and parses the given string if it fits to conditions.
        :return: The current word being parsed if it doesn't need to be parsed by the numbers rules
                    example: 138.31.21 could be self.word and would not fit to rules, but needs to be tokenized like this.
                    or the number after parse under the given rules.
        """
        token = self.word
        percent = False
        if token[-1] == '%':
            token = token[:-1]
            percent = True
        next_word = self.get_next_word()

        if next_word is not None and (next_word == 'Thousand' or next_word == 'Million' or next_word == 'Billion' or next_word == 'Trillion'):     # If there's a next word check it.
            token = self.parse_numbers_with_words(next_word)
        elif next_word is not None and next_word in self.data_byte_dictionary:  # If number is part of data presentation, don't parse it.
            return token
        else:
            if self.word.__contains__('-'):
                token = self.handle_range_with_number(token)
                #TODO: add to line both numbers in range to get parsed again.
            elif self.word.__contains__('/'):
                token = self.parse_fraction(self.word)
            elif self.word.__contains__(','):
                pattern = re.compile(r'(([1-9]\d{0,2},\d{3},\d{3},\d{3})|([1-9]\d{0,2},\d{3},\d{3})|([1-9]\d{0,2},\d{3}))')     #Numbers with comma
                token = pattern.sub(self.replace_only_numbers_regex, self.word)       #Substitute to parsed string
            elif self.word.__contains__('.'):
                pattern = re.compile(r'(([1-9]\d{9,11}\.\d{1,9})|([1-9]\d{6,8}\.\d{0,9})|([1-9]\d{3,5}\.\d{1,9}))')         #Numbers with decimal point
                token = pattern.sub(self.replace_only_numbers_regex, self.word)       #Substitute to parsed string
            elif self.is_integer(self.word):        # Normal number between 0-999 possibly
                if len(self.word) >= 4:
                    token = self.add_commas_to_integer(self.word)
                    pattern = re.compile(r'(([1-9]\d{0,2},\d{3},\d{3},\d{3})|([1-9]\d{0,2},\d{3},\d{3})|([1-9]\d{0,2},\d{3}))')  # Numbers with comma
                    token = pattern.sub(self.replace_only_numbers_regex, token)  # Substitute to parsed string
                else:
                    token = self.word

        if percent and token is not None:
            token = token + '%'

        return token

    def handle_range_with_number(self, token):
        """
        Method parses one or two numbers in range and adds them to collection
        :param token:  <number>-aString
        :return: the range token after parse
        """
        range_tokens = token.split('-')
        if len(range_tokens) == 2:
            parser = Parser([''], stem=self.stem)
            # parsed_tokens = self.create_tokens([''.join([range_tokens[0], ' ', range_tokens[1]])])
            parsed_tokens = parser.create_tokens([''.join([range_tokens[0], ' ', range_tokens[1]])])
            list_keys = list(parsed_tokens.keys())
            first_word = list_keys[0]
            second_word = ''

            if self.is_any_kind_of_number(first_word):
                self.add_token_to_collections(first_word, (self.data_index, self.line_index))

            if len(list_keys) == 2:             # *** There is case when: <number>-percent, because of a conflict in rules
                second_word = list_keys[1]      # we decided to go with the rule of <number>%
                if self.is_any_kind_of_number(second_word):
                    self.add_token_to_collections(second_word, (self.data_index, self.line_index))

            token = ''.join([first_word, '-', second_word])
        return token

    def add_commas_to_integer(self, number):
        """
        Method receives integer and adds comma's to it
        :param number: string
        :return: string number with correct comma seperation.
        """
        number_length = len(number)
        token = ''
        i = number_length - 1
        counter = 1
        while i >= 0:
            token = ''.join([number[i], token])
            if counter % 3 == 0 and i != 0:
                token = ''.join([',', token])
            counter += 1
            i -= 1
        return token

    def parse_range(self):
        # *** NEED TO FIX FUNCTION, CURRENTLY NOT IN USE ***
        after_split = self.word.split('-')
        if len(after_split) == 2:
            if (self.is_any_kind_of_number(after_split[0]) and self.is_any_kind_of_number(after_split[1])) or (self.is_any_kind_of_number(after_split[0]) and not self.is_any_kind_of_number(after_split[1])):
                # if it's <number>-<number> or <number>-<word or something not an umber>
                return self.word

    # TODO: Go over this function, check if you want maybe to parse the numbers in the fration or not.
    def parse_fraction(self, token):
        """
        Parses fraction number
        :return: ready token:<number> <fraction> or just <fraction>
        """
        after_split = token.split('/')
        if len(after_split) == 2:
            numerator = after_split[0]
            denominator = after_split[1]
            if (self.is_integer(numerator) or self.is_float(numerator)) and (self.is_integer(denominator) or self.is_float(denominator)):  # If it's <int>/<int>
                if len(self.tokens) >= 1:
                    previous_word = self.tokens[-1]
                    if self.is_any_kind_of_number(previous_word):
                        self.delete_token_i(1)  # Delete tokenized number to tokenize number with fraction as single token
                        # del self.tokens[-1]
                        return previous_word + ' ' + token
                    else:
                        return token

        return token

    def parse_numbers_with_words(self, next_word):
        """
        Parses numbers with the words Trillion Billion Million and Thousand
        :param next_word:
        :return:
        """
        pattern = None
        if next_word == 'Trillion':
            pattern = re.compile(r'([1-9]\d{0,2}\sTrillion)')
        elif next_word == 'Billion':
            pattern = re.compile(r'([1-9]\d{0,2}\sBillion)')
        elif next_word == 'Million':
            pattern = re.compile(r'([1-9]\d{0,2}\sMillion)')
        elif next_word == 'Thousand':
            pattern = re.compile(r'([1-9]\d{0,2}\sThousand)')
        if pattern is not None:
            self.skip_tokenize = 1
            return pattern.sub(self.replace_numbers_with_words_regex, self.word + next_word)  # Substitute to parsed string

    def parse_dollar_sign_with_number(self):
        """
        Parses words like: $<number>
        :return: token: <number> Dollars
        """
        token = self.word
        next_word = self.get_next_word()
        price = self.word[1:]       # only number without $ sign

        if next_word is not None and len(next_word) > 0:
            if next_word == 'million' or next_word == 'billion' or next_word == 'trillion':
                if self.is_integer(price) or self.is_float(price):
                    token = self.parse_dollar_sign_with_parsed_number_million(('$', price, next_word))
                    # *** Here need to skip next token to not tokenize it
                    self.skip_tokenize = 1
            else:
                token = self.parse_numbers_for_dollar_sign(price)
        else:
            token = self.parse_numbers_for_dollar_sign(price)

        return token

    def parse_numbers_for_dollar_sign(self, price):
        """
        Method parses the number of the dollar by demand - ONLY IF IT IS A NUMBER, if not it returns $andwhateverwashere
        :param price: the number only without $ sign
        :return: <number> Dollars
        """
        number_indicator = False        #Helps us know if current price is a string which is a number
        if price.__contains__('/'):
            return self.parse_fraction_dollar_sign(price)
        raw_number_str = price.replace(',', '')
        if raw_number_str.__contains__('.') and self.is_float(raw_number_str):
            raw_number = float(raw_number_str)
            number_indicator = True
        elif self.is_integer(raw_number_str):
            raw_number = int(raw_number_str)
            number_indicator = True
        if number_indicator:
            if 1000 <= raw_number < 1000000:        #Only thousands
                pattern = re.compile(r'(([1-9]\d{0,2},\d{3})|([1-9]\d{3,5}\.\d{1,9}))')
                price = pattern.sub(self.replace_only_thousands_dollars_regex, price)
                price = price + ' Dollars'

            elif raw_number >= 1000000:             #Millions and above
                pattern = re.compile(r'([1-9]\d{0,2},\d{3},\d{3},\d{3})|([1-9]\d{0,2},\d{3},\d{3})|([1-9]\d{9,11}\.\d{1,9})|([1-9]\d{6,8}\.\d{0,9})')
                price = pattern.sub(self.replace_only_millions_above_dollars_regex, price)
                price = self.parse_dollar_sign_with_parsed_number_million(('$', price))

            else:
                price = price + ' Dollars'
            return price
        return '$' + price

    def parse_dollar_sign_with_parsed_number_million(self, tokens):
        """
        Parses rules 2,3,4,5 (prices with the char $ not in thousands)
        :param tokens: list of $ <parsed_number>  or $ <number> <million/billion/trillion>
        :return: <number> M Dollars
        """
        token_str = str(tokens[1])
        if len(tokens) > 2:             # if $ <number> <million/billion/trillion>
            if tokens[2] == 'million':
                token_str = token_str + 'M'
            elif tokens[2] == 'billion':
                token_str = token_str + 'B'
            elif tokens[2] == 'trillion':
                token_str = token_str + 'T'
                # $price  only   $ <number>
        m_position = token_str.find('M')
        b_position = token_str.find('B')
        t_position = token_str.find('T')
        dot_position = token_str.find('.')
        if m_position != -1:     # $12M or $14.5M to 12 M Dollars or 14.5 M Dollars
            token_str = token_str[0:m_position] + ' M Dollars'
        elif b_position != -1:   #  $15B
            if dot_position != -1:      #  $15.27B
                dist = b_position - dot_position
                token_str = token_str.replace('.', '')
                if dist == 2:
                    token_str = token_str[0:b_position-1] + '00 M Dollars'
                elif dist == 3:
                    token_str = token_str[0:b_position-1] + '0 M Dollars'
                elif dist == 4:
                    token_str = token_str[0:b_position-1] + ' M Dollars'
            else:
                token_str = token_str[0:b_position] + '000 M Dollars'
        elif t_position != -1:          #  $12.7T  5T   to 12700 M Dollars and 5000000 M Dollars
            if dot_position != -1:
                dist = t_position - dot_position
                token_str = token_str.replace('.', '')
                if dist == 2:
                    token_str = token_str[0:t_position-1] + '00000 M Dollars'
                elif dist == 3:
                    token_str = token_str[0:t_position-1] + '0000 M Dollars'
                elif dist == 4:
                    token_str = token_str[0:t_position-1] + '000 M Dollars'
            token_str = token_str[0:t_position] + '000000 M Dollars'
        return token_str

    def replace_numbers_with_words_regex(self, match):
        """
        Method which replaces each case of number to the correct representation
        :param match: The match found by the regex
        :return: After substitute
        """
        value = match.group()
        value_str = str(value)
        dot_position = value_str.find('.')
        if "Thousand" in value_str or (dot_position > 0 and 2 < len(value_str[0:dot_position]) < 7):
            return self.replace_thousands(value_str)
        elif "Million" in value_str or (dot_position > 0 and 6 < len(value_str[0:dot_position]) < 10):
            return self.replace_millions(value_str)
        elif "Billion" in value_str or (dot_position > 0 and 9 < len(value_str[0:dot_position]) < 13):
            return self.replace_billions(value_str)
        elif "Trillion" in value_str or "." in value_str:
            return self.replace_trillion(value_str)

    def replace_only_numbers_regex(self, match):
        """
        Method is called when regex for normal numbers has a match
        :param match: string
        :return: parsed number
        """
        value = match.group()
        value_str = str(value)
        value_int = float(value_str.replace(',', ''))
        if value_int < 1000000:
            return self.replace_thousands(value_str)
        elif value_int < 1000000000:
            return self.replace_millions(value_str)
        elif value_int < 1000000000000:
            return self.replace_billions(value_str)

    def replace_only_millions_above_dollars_regex(self, match):
        """
        Method is called when regex for numbers for currency (dollars) parsing
        :param match: string
        :return: parsed number according to dollars rules
        """
        value = match.group()
        value_str = str(value)
        value_int = float(value_str.replace(',', ''))
        if value_int < 1000000000:
            return self.replace_millions(value_str)
        elif value_int < 1000000000000:
            return self.replace_billions(value_str)

    def replace_only_thousands_dollars_regex(selfs, match):
        """
        Method is called when regex for thousands of currency (dollars) found a match.
        :param match: string
        :return: parsed number
        """
        value = match.group()
        value_str = str(value)
        value_int = float(value_str.replace(',', ''))
        if value_int < 1000000:
            return value_str

    def replace_trillion(self, value):
        """
        Replaces Trillions: when regex found a number in trillions and parses it according to the rules.
        :param value: String value of the number
        :return: String after parsing
        """
        # value = match.group()
        str_value = value
        str_value = str_value.split(' ')[0] + 'T'
        return str_value

    def replace_thousands(self, value):
        """
        Replaces thousands: when regex found a number in thousands and parses it according to the rules.
        :param value: String value of the number: either with comma or with "Thousand" or with '.'.
        :return: String after parsing
        """
        # value = match.group()
        str_value = value
        if "," in str_value:
            str_after_split = str_value.split(',')
            if not str_after_split[1] == '000':
                thousands = str_after_split[0]
                after_decimal_point = str_after_split[1].rstrip('0')
                if len(after_decimal_point) > 2:     # No more than 2 digits after decimal point
                    after_decimal_point = after_decimal_point[:2]
                str_value = thousands + '.' + after_decimal_point + 'K'  # if not <int>,<int>{3}
            else:
                str_value = str_value.split(',')[0] + 'K'  # if x,000 when x =[1-9]
        elif str_value.__contains__("Thousand"):
            str_value = str_value.split(' ')[0] + 'K'  # if <int> Thousand
        elif str_value.__contains__("."):  # if number has a decimal point '.'
            comma_position = str_value.find(".")
            beginning = str_value[0:comma_position - 3]
            middle = str_value[comma_position - 3:comma_position]
            end = str_value[comma_position + 1:]
            after_decimal_point = middle + end
            if len(after_decimal_point) > 2:     #No more than 2 digits after decimal point
                after_decimal_point = after_decimal_point[:2]
            str_value = beginning + "." + after_decimal_point + "K"
        return str_value

    def replace_millions(self, value):
        """
        Replaces millions: when regex found a match for millions and it parses it according to the rules.
        :param value: String value of the number
        :return: String after parsing
        """
        # value = match.group()
        str_value = value
        if str_value.__contains__(","):
            str_after_split = str_value.split(",")
            if str_after_split[2] == '000':
                if str_after_split[1] == '000':  # If 5,000,000
                    str_value = str_after_split[0] + 'M'
                else:  # if 5,204,000
                    millions = str_after_split[0]
                    after_decimal_point = str_after_split[1].rstrip('0')
                    if len(after_decimal_point) > 2:       # No more than 2 digits after decimal point.
                        after_decimal_point = after_decimal_point[:2]
                    str_value = millions + '.' + after_decimal_point + 'M'
            else:  # if 5,203,400
                millions = str_after_split[0]
                after_decimal_point = str_after_split[1] + str_after_split[2].rstrip('0')
                if len(after_decimal_point) > 2:     # No more than 2 digits after decimal point.
                    after_decimal_point = after_decimal_point[:2]
                str_value = millions + '.' + after_decimal_point + "M"
        elif str_value.__contains__("Million"):
            str_value = str_value.split(' ')[0] + 'M'
        elif str_value.__contains__('.'):
            comma_position = str_value.find('.')
            beginning = str_value[0:comma_position - 6]
            middle = str_value[comma_position - 6:comma_position]
            end = str_value[comma_position + 1:]
            after_decimal_point = middle + end
            if len(after_decimal_point) > 2:     # No more than 2 digits after decimal point
                after_decimal_point = after_decimal_point[:2]
            str_value = beginning + "." + after_decimal_point + "M"
        return str_value

    def replace_billions(self, value):
        """
        Replaces billions: when regex found a match and parses it acording to the rules.
        :param value: String value of the number
        :return: String after parsing
        """
        # value = match.group()
        str_value = value
        if str_value.__contains__(','):
            str_after_split = str_value.split(',')
            after_decimal_point = ''
            if str_after_split[3] == str_after_split[2] == str_after_split[1] == '000':
                str_value = str_after_split[0] + 'B'
            elif str_after_split[3] == str_after_split[2] == '000':
                after_decimal_point = str_after_split[1].rstrip('0')
                # str_value = str_after_split[0] + '.' + after_decimal_point + 'B'
            elif str_after_split[3] == '000':
                after_decimal_point = str_after_split[1] + str_after_split[2].rstrip('0')
                # str_value = str_after_split[0] + '.' + after_decimal_point + 'B'
            else:
                after_decimal_point = str_after_split[1] + str_after_split[2] + str_after_split[3].rstrip('0')
                # str_value = str_after_split[0] + '.' + after_decimal_point + 'B'
            if len(after_decimal_point) > 2:     # No more than 2 digits after decimal point
                after_decimal_point = after_decimal_point[:2]
            str_value = str_after_split[0] + '.' + after_decimal_point + 'B'
        elif str_value.__contains__('Billion'):
            str_value = str_value.split(' ')[0] + 'B'
        return str_value


    def change_day_format(self, s):
        """
        If s is a number between 1-9 add the digit 0 at beginning
        :param s: string
        :return: string day representation according to rules
        """
        if len(s) == 1:
            return '0' + s
        else:
            return s

    def is_any_kind_of_number(self, s):
        """
        Method checks if given string s is either Integer, Float or a parsed number
        :param s:
        :return:
        """
        if s is None or len(s) == 0:
            return False
        return self.is_number_k_m_b_t(s) or self.is_integer(s) or self.is_float(s)


    def is_integer(self, s):
        """
        Checks if string s is int
        :param s: string
        :return: True/False
        """
        if s is None or len(s) == 0:
            return False
        try:
            int(s)
            return True
        except ValueError:
            return False

    def is_float(self, s):
        """
        Checks if string s is float
        :param s: string
        :return: True/False
        """
        if s is None or len(s) == 0:
            return False
        try:
            float(s)
            return True
        except ValueError:
            return False

    def is_number_k_m_b_t(self, s):
        """
        Checks if string s is Thousands/Millions/Billions/Trillions
        :param s: string representation
        :return: True/False
        """
        if s is None or len(s) == 0:
            return False
        value_str = str(s)
        str_length = len(value_str)

        letter = value_str[str_length-1]
        if letter == 'K' or letter == 'M' or letter == 'B':
            try:
                float(value_str[0:str_length-1])
                return True
            except ValueError:
                return False
        elif value_str[str_length-1] == 'T':
            try:
                int(value_str[0:str_length-1])
                return True
            except ValueError:
                return False

    def parse_fraction_dollar_sign(self, token):
        """
        Parses fraction number
        :return: ready token:<number> <fraction> or just <fraction>
        """
        after_split = token.split('/')
        if len(after_split) == 2:
            numerator = after_split[0]
            denominator = after_split[1]
            if (self.is_integer(numerator) or self.is_float(numerator)) and (
                    self.is_integer(denominator) or self.is_float(denominator)):  # If it's <int>/<int>
                        return token + ' Dollars'
        return '$' + token

    def get_tokens_after_parse(self):
        """
        Method returns a list of all parsed tokens.
        We use this when we want to consider multiple appearances of the terms instead of considering
        only one appearance as in dictionary
        :return: List of Tokens
        """
        return self.tokens