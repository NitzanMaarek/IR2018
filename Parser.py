import re
import time
import locale

import datetime
from nltk.tokenize import word_tokenize
from nltk.stem.porter import *

class Parser:

    static_stop_words_list = []

    def __init__(self):
        self.percent_key_words = ('%', 'percent', 'percentage')
        self.dollar_key_words = ('$', 'Dollars', 'dollars')
        self.month_dictionary = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
                                 'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12',
                                 'JANUARY': '01', 'FEBRUARY': '02', 'MARCH': '03', 'APRIL': '04', 'MAY': '05', 'JUNE': '06', 'JULY': '07',
                                 'AUGUST': '08', 'SEPTEMBER': '09', 'OCTOBER': '10', 'NOVEMBER': '11', 'DECEMBER': '12'}
        self.month_first_letter_array = ['a', 'A', 'd', 'D', 'f', 'F', 'j', 'J', 'm', 'M', 'n', 'N', 'o', 'O', 's', 'S']
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        self.delimiters = [' ', ',', '.', '/', '"', '\'', '\\', '(', ')', '[', ']', '{', '}', ':', '-', ';']
        self.token_index = 0
        self.word = ''
        self.line_index = 0     # Index of words in a line
        self.line = ''
        self.data_index = 0     # Index of lines in data
        self.data = None


    def parser_pipeline(self, data, stem):
        self.data = data
        tokens = self.create_tokens(self.data)
        # tokens = self.find_key_words_in_line(tokens)
        if stem:
            stemmer = PorterStemmer()
            tokens = [stemmer.stem(term) for term in tokens]
        return tokens

    def create_tokens(self, data):
        tokens = []
        for data_index, line in enumerate(data, start=0):
            self.data_index = data_index
            self.line = line.split()
            for line_index, word in enumerate(self.line, start=0):
                self.line_index = line_index
                self.word = word
                last = len(word) - 1
                first = 0
                while first <= last and (
                        word[last] in self.delimiters or self.word[first] in self.delimiters):  # loop to remove delimiters
                    if word[first] in self.delimiters:
                        first += 1
                    if word[last] in self.delimiters:
                        last -= 1
                if first > last:  # Means all word was delimiters and need to ignore it.
                    continue
                else:  # Means not all of the word is delimiters
                    word = word[first:last + 1]
                self.word = word
                if self.word in Parser.static_stop_words_list:
                    continue

            # Here we're supposed to have the word (not stop-word) without any delimiters
            # Word is normal word and also String with delimiters in inside: number with comma, words with slash etc..

            token = self.parse_strings()
            if token is not None and len(token) > 0:
                tokens.append(token)


        return tokens

    def get_next_word(self):
        """
        iterates over data if next word exists and returns it
        :return: next word in data, None if end of text.
        """
        if self.line_index == len(self.line) - 1:                   #If current word is last in line
            if len(self.data) > self.data_index + 1:                #If current line is NOT last line
               return self.data[self.data_index + 1][0]          #Take next word in next line in case its important
        return None

    def get_previous_word(self):
        if self.data_index != 0:
            return self.data[self.data_index - 1][0]
            #TODO: need to check if previous doesn't return \n



    def parse_strings(self):
        token = self.word
        if token is None or len(token) == 0:
            return None

        first_token = token[0]
        if first_token == '1' or first_token == '2' or first_token == '3' or first_token == '4' or first_token == '5' or first_token == '6' or first_token == '7' or first_token == '8' or first_token == '9':
            token = self.parse_string_only_number()
        if first_token == '$':
            token = self.parse_dollar_sign_with_number()
        if (first_token == 'd' or first_token == 'D') and (token == 'dollars' or token == 'Dollars'):
            token = self.parse_dollar_sign_with_number
        if (first_token == 'b' or first_token == 'B') and (token == 'Between' or token == 'between'):

        if token in self.month_dictionary.keys():

        if (first_token == 'p' or first_token == 'P') and (token == 'percent' or token == 'Percent' or token == 'percentage' or token == 'Percentage'):

        return token


    def parse_string_only_number(self):
        """
        Method checks and parses the given string if it fits to conditions.
        :return: The current word being parsed if it doesn't need to be parsed by the numbers rules
                    example: 138.31.21 could be self.word and would not fit to rules, but needs to be tokenized lik this.
                    or the number after parse under the given rules.
        """
        token = self.word
        next_word = ''
        pattern = None

        if self.line_index == len(self.line) - 1:                   #If current word is last in line
            if len(self.data) > self.data_index + 1:                #If current line is NOT last line
                next_word = self.data[self.data_index + 1][0]         #Take next word in next line in case its important
                #TODO: check that command above really takes first word in next line.
        else:                                                       #Current word is not last in line
            next_word = self.line[self.line_index + 1]              #Take next word in line also

        if not next_word == '':     # If there's a next word check it.
            token = self.parse_numbers_with_words()
        else:
            if self.word.__contains__('-'):
                # token = self.parse_range()
                token = self.word
            elif self.word.__contains__('/'):
                token = self.parse_fraction()
            elif self.word.__contains__(','):
                pattern = re.compile(r'(([1-9]\d{0,2},\d{3},\d{3},\d{3})|([1-9]\d{0,2},\d{3},\d{3})|([1-9]\d{0,2},\d{3}))')     #Numbers with comma
                token = pattern.sub(self.replace_only_numbers_regex(), self.word)       #Substitute to parsed string
            elif self.word.__contains__('.'):
                pattern = re.compile(r'(([1-9]\d{9,11}\.\d{1,9})|([1-9]\d{6,8}\.\d{0,9})|([1-9]\d{3,5}\.\d{1,9}))')         #Numbers with decimal point
                token = pattern.sub(self.replace_only_numbers_regex(), self.word)       #Substitute to parsed string
            else:
                pattern = re.compile(r'(([1-9]\d{0,2}\.\d{1,9})|([1-9]\d{0,2}))')       #Number between 0-999 possible decimal point
                token = pattern.match()
                # TODO: Check if two lines above work for numbers between 0 and 999 with decimal point also.

        return token

    def parse_range(self):
        after_split = self.word.split('-')
        if len(after_split) == 2:
            if (self.is_any_kind_of_number(after_split[0]) and self.is_any_kind_of_number(after_split[1])) or (self.is_any_kind_of_number(after_split[0]) and not self.is_any_kind_of_number(after_split[1])):
                # if it's <number>-<number> or <number>-<word or something not an umber>
                return self.word

    def parse_fraction(self):
        """
        Parses fraction number
        :return: ready token:<number> <fraction> or just <fraction>
        """
        after_split = self.word.split('/')
        if len(after_split) == 2:
            if self.is_integer(after_split[0]) and self.is_integer(after_split[1]):     #If it's <int>/<int>
                if self.data_index != 0:
                    previouse_word = self.data[self.data_index - 1][0]      # TODO: Need to check previous_word != '\n'
                    if self.is_any_kind_of_number(previouse_word):
                        return previouse_word + self.word
                    else:
                        return self.word
        else:
            return self.word

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
            return pattern.sub(self.replace_numbers_with_words_regex, self.word + next_word)  # Substitute to parsed string

    def parse_dollar_sign_with_number(self):
        """
        Parses words like: $<number>
        :return: token: <number> Dollars
        """
        token = self.word
        next_word = ''
        price = self.word[1:]

        if not self.line_index == len(self.line) - 1:                   #If current word is not last in line
            next_word = self.line[self.line_index + 1]                  # Take next word in line
        else:
            ka = 1
            #TODO: need to take the first word from next line

        if not len(next_word) == 0:
            if next_word == 'million' or next_word == 'billion' or next_word == 'trillion':
                if 1 < len(price) < 4 and (self.is_integer(price) or self.is_float(price)):
                    token = self.parse_dollar_sign_with_word(('$', price, next_word))
        else:
            price = self.parse_numbers_for_dollar_sign(price)





        token_str = str(tokens[i])
        if token_str == '$':  # if tokens contain sign $
            if len(tokens) > i + 2 and (
                    tokens[i + 2] == 'million' or tokens[i + 2] == 'billion' or tokens[i + 2] == 'trillion'):
                tokens[i] = self.sub_currency_in_line(
                    (tokens[i], tokens[i + 1], tokens[i + 2]))  # parse $ <number> <million/billion/trillion>
                del tokens[i + 1]
                del tokens[i + 1]
                # self.token_index = self.token_index - 1
            elif str(tokens[i + 1]).__contains__('K') or str(tokens[i + 1]).__contains__('M') or str(
                    tokens[i + 1]).__contains__('B') or str(tokens[i + 1]).__contains__('T'):
                tokens[i] = self.sub_currency_in_line((tokens[i], tokens[i + 1]))  # parse $ <number>
                del tokens[i + 1]
            else:
                tokens[i] = tokens[i + 1] + ' Dollars'
                del tokens[i + 1]

    def parse_numbers_for_dollar_sign(self, price):
        """
        parses the number of the dollar by demand
        :param price: the number
        :return: only the number in currency format
        """
        dot_position = price.find('.')
        comma_position = price.find(',')

        if price.__contains__(','):
            pattern = re.compile(r'(([1-9]\d{0,2},\d{3},\d{3},\d{3})|([1-9]\d{0,2},\d{3},\d{3}))')  # Numbers with comma
            price = pattern.sub(self.replace_only_numbers_regex(), self.word)  # Substitute to parsed string

        elif self.word.__contains__('.'):
            pattern = re.compile(r'(([1-9]\d{9,11}\.\d{1,9})|([1-9]\d{6,8}\.\d{0,9})|([1-9]\d{3,5}\.\d{1,9}))')  # Numbers with decimal point
            price = pattern.sub(self.replace_only_numbers_regex(), self.word)  # Substitute to parsed string

        else:
            pattern = re.compile(r'(([1-9]\d{0,2},\d{3})|(([1-9]\d{3,5}\.\d{1,9}))|([1-9]\d{0,2}\.\d{1,9})|([1-9]\d{0,2}))')  # Number between 0-999 possible decimal point
            price = pattern.match()


    def parse_dollar_sign_with_word(self, tokens):
        """
        Parses rules 2,3,4,5 (prices with the char $ not in thousands)
        :param tokens: list of
        :return: the correct and final token
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
        Function which replaces each case of number to the correct representation
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
        value = match.group()
        value_str = str(value)
        value_int = int(value_str.replace(',', ''))
        if value_int < 1000000:
            return self.replace_thousands(value_str)
        elif value_int < 1000000000:
            return self.replace_millions(value_str)
        elif value_int < 1000000000000:
            return self.replace_billions(value_str)

    def replace_trillion(self, value):
        """
        Replaces Trillions
        :param value: String value of the number
        :return: String after parsing
        """
        # value = match.group()
        str_value = value
        str_value = str_value.split(' ')[0] + 'T'
        return str_value

    def replace_thousands(self, value):
        """
        Replaces thousands
        :param value: String value of the number
        :return: String after parsing
        """
        # value = match.group()
        str_value = value
        if "," in str_value:
            if not str_value.split(',')[1] == '000':
                str_value = str_value.split(',')[0] + '.' + str_value.split(',')[1].rstrip(
                    '0') + 'K'  # if not <int>,<int>{3}
            else:
                str_value = str_value.split(',')[0] + 'K'  # if <int>,000 when x =[1-9]
        elif str_value.__contains__("Thousand"):
            str_value = str_value.split(' ')[0] + 'K'  # if <int> Thousand
        elif str_value.__contains__("."):  # if number has no comma (,)
            comma_position = str_value.find(".")
            beginning = str_value[0:comma_position - 3]
            middle = str_value[comma_position - 3:comma_position]
            end = str_value[comma_position + 1:]
            str_value = beginning + "." + middle + end + "K"
        return str_value

    def replace_millions(self, value):
        """
        Replaces millions
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
                    str_value = str_after_split[0] + '.' + str_after_split[1].rstrip('0') + 'M'
            else:  # if 5,203,400
                str_value = str_after_split[0] + '.' + str_after_split[1] + str_after_split[2].rstrip('0') + "M"
        elif str_value.__contains__("Million"):
            str_value = str_value.split(' ')[0] + 'M'
        elif str_value.__contains__('.'):
            comma_position = str_value.find('.')
            beginning = str_value[0:comma_position - 6]
            middle = str_value[comma_position - 6:comma_position]
            end = str_value[comma_position + 1:]
            str_value = beginning + "." + middle + end + "M"
        return str_value

    def replace_billions(self, value):
        """
        Replaces billions
        :param value: String value of the number
        :return: String after parsing
        """
        # value = match.group()
        str_value = value
        if str_value.__contains__(','):
            str_after_split = str_value.split(',')
            if str_after_split[3] == str_after_split[2] == str_after_split[1] == '000':
                str_value = str_after_split[0] + 'B'
            elif str_after_split[3] == str_after_split[2] == '000':
                str_value = str_after_split[0] + '.' + str_after_split[1].rstrip('0') + 'B'
            elif str_after_split[3] == '000':
                str_value = str_after_split[0] + '.' + str_after_split[1] + str_after_split[2].rstrip('0') + 'B'
            else:
                str_value = str_after_split[0] + '.' + str_after_split[1] + str_after_split[2] + str_after_split[3].rstrip('0') + 'B'
        elif str_value.__contains__('Billion'):
            str_value = str_value.split(' ')[0] + 'B'
        return str_value







    def sub_currency_in_line(self, tokens):
        """
        Function returns tokenized token of price with given tokens list
        :param tokens: Tokens of regarding parsing price ONLY.  Length of list is either 2 or 3 elements
                        Tokens will hold either: ('$', <number>) or ('$', <number>, <million/billion/trillion>)
        :return: new token after parse
        """
        first_token_str = str(tokens[0])
        second_token_str = str(tokens[1])
        if second_token_str.__contains__('K'):               # if price in thousands SUBSTITUTE AND RETURN CORRECT TOKEN
            if first_token_str.__contains__('$'):           # if $450K or $12.1K
                second_token_str = self.sub_currency_k(second_token_str)    # returns $450,000 or $12,100
                second_token_str = second_token_str + ' Dollars'
            else:
                second_token_str = self.sub_currency_k(second_token_str)    #if 450K Dollars or 12.1K Dollars, returns 450,000 dollars etc. (HAS THE WORD DOLLARS)
            return second_token_str                   # return fixed token
        else:
            return self.parse_dollar_sign_with_word(tokens)   # *** NEED TO SEND ONLY $PRICE TOKENS LIST***



    def change_day_format(self, s):
        if len(s) == 1:
            return '0' + s
        else:
            return s

    def is_any_kind_of_number(self, s):
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