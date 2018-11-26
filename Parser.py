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
        self.skip_tokenize = 0  # Indicates how many tokens to skip to not tokenize


    def parser_pipeline(self, data, stem):
        self.data = data
        tokens = self.create_tokens(self.data)
        # tokens = self.find_key_words_in_line(tokens)
        if stem:
            stemmer = PorterStemmer()
            tokens = [stemmer.stem(term) for term in tokens]
        return tokens

    def create_tokens(self, data):
        self.tokens = []
        skip_tokenize = 0
        self.data_length = len(data)
        self.between_flag = False
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
                    token = self.parse_handle_between_token(token)   # If we've encountered the word between then keep track if next tokens are : between <number> and <number>
                    self.tokens.append(token)

        return self.tokens

    def parse_handle_between_token(self, parsed_token):
        """
        If we've encountered the word between then keep track if next tokens are : between <number> and <number>
        between index 1 is 'between', 2 is the first number, 3 is 'and', and 4is the last number
        :param parsed_token: token parsed
        :return: token 'between <number> and <number>' after deletion if sequence complete, normal token otherwise
        """
        token = parsed_token
        if not self.between_flag and (token == 'between' or token == 'Between'):
            self.between_flag = True
            self.between_index = 1
        elif self.between_flag and self.between_index > 1:  # If word between appeared check next strings
            if self.between_index == 3 and token == 'and':  # If its time for the word 'and' to appear
                self.between_index += 1
            elif (self.between_index == 2 or self.between_index == 4) and self.is_any_kind_of_number(token):  # If number
                self.between_index += 1
            else:
                if self.between_index == 5:  # if between <number> and <number> sequence appeard, token it and delete previous 3 tokens (current is number)
                    token = 'between ' + self.tokens[-2] + ' and ' + token
                    del self.tokens[-3]
                    del self.tokens[-2]
                    del self.tokens[-1]
                # Reset between sequence
                # *** IMPORTANT: if not 'and' or number where its supposed to be, reset between sequence by flag = False and index = 0
                self.between_index = 0
                self.between_flag = False
        return token

    def get_next_word(self):
        """
        iterates over data if next word exists and returns it
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
                    if last_char_next_word in self.delimiters:  # Check if next word contains delimiter as last char.
                        first_word_next_line = first_word_next_line[:-1]
                return first_word_next_line          #Take next word in next line in case its important
        else:
            next_word = self.line[self.line_index + 1]
            if next_word is not None:
                last_char_next_word = next_word[-1]
                if last_char_next_word in self.delimiters:  # Check if next word contains delimiter as last char.
                    next_word = next_word[:-1]
            return next_word           # Not last in line? return the next word in line then
        return None

    def get_word_i(self, i):
        """
        iterates over data if and returns item i from where we are if exists
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
        Assumption that there is a next line
        this method will iterate over empty lines until it reaches a line which is not empty
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



    def get_previous_word(self):
        if self.data_index != 0:
            return self.tokens[-1]
            #TODO: need to check if previous doesn't return \n

    def parse_strings(self):
        """
        Main parse function
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
        elif token in self.month_dictionary.keys():
            token = self.parse_date_with_month()
        elif (first_token == 'p' or first_token == 'P') and (token == 'percent' or token == 'Percent' or token == 'percentage' or token == 'Percentage'):
            token = self.parse_percent_word()
        return token

    def check_if_token_is_numer_range(self, token):
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
                if self.is_any_kind_of_number(first_number) and self.is_any_kind_of_number(second_number):
                    return True
        return False

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
        method marks to skip 1 token and return correct token
        :param date_list: (month, year)
        :return: token = <year>-<month>
        """
        token = date_list[1] + '-' + self.month_dictionary.get(date_list[0])
        self.skip_tokenize = 1
        return token

    def parse_day_after_month(self, date_list):
        """
        method marks to skip next tokenize and returns correct token
        :param date_list: (day, month)
        :return: token = <month>-<day>
        """
        token = self.month_dictionary.get(date_list[1]) + '-' + self.change_day_format(date_list[0])
        self.skip_tokenize = 1
        return token

    def parse_day_before_month_no_year(self, date_list):
        """
        this method deletes previous (day) and returns <month>-<day>
        :param date_list: (day, month) = no need to check input
        :return: token = <month>-<day>
        """
        token = self.month_dictionary.get(date_list[1]) + '-' + self.change_day_format(date_list[0])
        del self.tokens[-1]
        return token

    def parse_day_month_year(self, date_list):
        """
        this method will delete previous (day), mark to skip next (year), add 2 tokens and return the thirds to be appended.
        :param date_list: (day, month, year) = no need to check input
        :return: token: <year>-<month_number>-<day>
        """
        token = date_list[2] + '-' + self.month_dictionary.get(date_list[1]) + '-' + self.change_day_format(date_list[0])
        del self.tokens[-1]
        self.tokens.append(self.month_dictionary.get(date_list[1]) + '-' + self.change_day_format(date_list[0]))
        self.tokens.append(date_list[2] + '-' + self.month_dictionary.get(date_list[1]))
        self.skip_tokenize = 1
        return token

    def parse_percent_word(self):
        token = self.word
        if len(self.tokens) >= 1:
            previous_token = self.tokens[-1]
            if self.is_any_kind_of_number(previous_token):
                token = previous_token + '%'
                # *** Here need to delete last token which is the number and return <number>%
                del self.tokens[-1]
        return token

    def parse_dollar_with_capital_d(self):
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
                del self.tokens[-1]
            elif self.is_any_kind_of_number(previous_token):
                # TODO: THIS IS NOT GOOD NEED TO FIX THIS IN CASE OF THOUSANDS SINCE THEYRE ALREADY PARSED HERE
                price = str(previous_token)
                if price.__contains__('K'):
                    price = self.fix_thousands_for_dollars(price)
                    token = price + ' Dollars'
                elif price.__contains__('M') or price.__contains__('B') or price.__contains__('T'):
                    token = self.parse_dollar_sign_with_parsed_number_million(('$', previous_token))
                else:
                    token = price + ' Dollars'

                # *** Here need to delete last token which was the number because now adding <number> Dollars
                del self.tokens[-1]

        return token



    def fix_thousands_for_dollars(self, price_in_thousands):
        """
        Functions substitutes thousands of currency to correct format for currency
        :param price_in_thousands: string of price in thousands: 5.1k or 42k  (with comma or without)
        :return: correct string
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
                    del self.tokens[-3]
                    del self.tokens[-2]
                    del self.tokens[-1]
        return token

    def parse_string_only_number(self):
        """
        Method checks and parses the given string if it fits to conditions.
        :return: The current word being parsed if it doesn't need to be parsed by the numbers rules
                    example: 138.31.21 could be self.word and would not fit to rules, but needs to be tokenized lik this.
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
        else:
            if self.word.__contains__('-'):
                token = self.word
            elif self.word.__contains__('/'):
                token = self.parse_fraction()
            elif self.word.__contains__(','):
                pattern = re.compile(r'(([1-9]\d{0,2},\d{3},\d{3},\d{3})|([1-9]\d{0,2},\d{3},\d{3})|([1-9]\d{0,2},\d{3}))')     #Numbers with comma
                token = pattern.sub(self.replace_only_numbers_regex, self.word)       #Substitute to parsed string
            elif self.word.__contains__('.'):
                pattern = re.compile(r'(([1-9]\d{9,11}\.\d{1,9})|([1-9]\d{6,8}\.\d{0,9})|([1-9]\d{3,5}\.\d{1,9}))')         #Numbers with decimal point
                token = pattern.sub(self.replace_only_numbers_regex, self.word)       #Substitute to parsed string
            elif self.is_integer(self.word):        # Normal number between 0-999 possibly
                token = self.word

        if percent and token is not None:
            token = token + '%'

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
                if len(self.tokens) >= 1:
                    previous_word = self.tokens[-1]      # TODO: Need to check previous_word != '\n'
                    if self.is_any_kind_of_number(previous_word):
                        del self.tokens[-1]
                        return previous_word + ' ' + self.word
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
                if 1 <= len(price) <= 3  and (self.is_integer(price) or self.is_float(price)):
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
        parses the number of the dollar by demand - ONLY IF IT IS A NUMBER, if not it returns $andwhateverwashere
        :param price: the number only without $ sign
        :return: <number> Dollars
        """
        number_indicator = False        #Helps us know if current price is a string which is a number
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
        value_int = float(value_str.replace(',', ''))
        if value_int < 1000000:
            return self.replace_thousands(value_str)
        elif value_int < 1000000000:
            return self.replace_millions(value_str)
        elif value_int < 1000000000000:
            return self.replace_billions(value_str)

    def replace_only_millions_above_dollars_regex(self, match):
        value = match.group()
        value_str = str(value)
        value_int = float(value_str.replace(',', ''))
        if value_int < 1000000000:
            return self.replace_millions(value_str)
        elif value_int < 1000000000000:
            return self.replace_billions(value_str)

    def replace_only_thousands_dollars_regex(selfs, match):
        value = match.group()
        value_str = str(value)
        value_int = float(value_str.replace(',', ''))
        if value_int < 1000000:
            return value_str

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


