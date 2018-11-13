import re
import time
import locale

class Parse:

    def __init__(self):

        self.percent_key_words = ('%', 'percent', 'percentage')
        self.dollar_key_words = ('$', 'Dollars', 'dollars')
        # self.month_list = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
        # self.month_list_capital = ('JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', ' OCTOBER', 'NOVEMBER', 'DECEMBER')
        self.month_dictionary = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
                                 'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12',
                                 'JANUARY': '01', 'FEBRUARY': '02', 'MARCH': '03', 'APRIL': '04', 'MAY': '05', 'JUNE': '06', 'JULY': '07',
                                 'AUGUST': '08', 'SEPTEMBER': '09', 'OCTOBER': '10', 'NOVEMBER': '11', 'DECEMBER': '12'}

        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        self.token_index = 0

    def regex_pipeline(self, data):
        # TODO: need to write method
        new_data = data
        return self.find_key_words_in_line(new_data)


    def is_number(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False


    def find_key_words_in_line(self, tokens):
        """
        Main function which runs after regex on numbers was activated on line
        This function finds special keywords that need to analyze in order to parse in a certain rule/way
        :param tokens: List of tokens to parse
        :return: Correct list of tokens AFTER parse
        """
        self.token_index = 0
        while self.token_index < len(tokens):
            token = tokens[self.token_index]
            token_str = tokens[self.token_index]
            if token_str == 'ratings':
                print('delete me and the if')
            if token_str in self.percent_key_words:                                 # If percent
                if token_str == ('percent' or 'percentage'):
                    tokens[self.token_index-1] = tokens[self.token_index-1] + '%'
                    del tokens[self.token_index]
                    self.token_index = self.token_index - 1
                else:
                    if self.token_index > 0:
                        if self.is_number(tokens[self.token_index-1]):
                            tokens[self.token_index-1] = tokens[self.token_index-1] + '%'
                            del tokens[self.token_index]
                            self.token_index = self.token_index - 1
            elif token_str in self.dollar_key_words:                            # If currency
                        self.tokenize_dollars(tokens, self.token_index)
            elif token_str in self.month_dictionary.keys():  # If date
                self.sub_dates_in_line(tokens, self.token_index)
            elif token[0] is ['A-Z']:           # *****CONDITION DOESNT WORK *****                                # If word begins with capital letter
                k = 1
            elif str(token).__contains__('-'):                                  # If word has a hyphen: adjacent words
                # self.sub_adjacent_tokens(tokens, i)
                j = 2
            self.token_index = self.token_index+1




    def parse_and_sub_numbers(self, line):
        """
        For each line use regex to identify and substitute numbers
        :param line: Text we want to parse
        :return: new line after parsing and substituting
        """
        # First pattern of Thousands, then Millions, then Billions and finally Trillions.
        pattern = re.compile(r'(([1-9]\d{0,2},\d{3},\d{3},\d{3})|([1-9]\d{9,11}\.\d{1,9})|([1-9]\d{0,2}\sBillion))|'
                             r'(([1-9]\d{0,2},\d{3},\d{3})|([1-9]\d{6,8}\.\d{0,9})|([1-9]\d{0,2}\sMillion))|'
                             r'(([1-9]\d{0,2},\d{3})|([1-9]\d{3,5}\.\d{1,9})|([1-9]\d{0,2}\sThousand))|'
                             r'([1-9]\d{0,2}\sTrillion)')
        line = pattern.sub(self.replace_numbers, line)
        # print(self.text)
        return line

    def replace_numbers(self, match):
        """
        Function which replaces each case of number to the correct representation
        :param match: The match found by the regex
        :return: After substitute
        """
        value = match.group()
        value_str = str(value)
        if "Thousand" in value_str or "." in value_str:
            return self.replace_thousands(value_str)
        elif "Million" in value_str or "." in value_str:
            return self.replace_millions(value_str)
        elif "Billion" in value_str or "." in value_str:
            return self.replace_billions(value_str)
        elif "Trillion" in value_str or "." in value_str:
            return self.replace_trillion(value_str)
        value_int = int(str(value).replace(',', ''))
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
            comma_position = str_value.index(".")
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
            comma_position = str_value.index('.')
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
                str_value = str_after_split[0] + '.' + str_after_split[1] + str_after_split[2] + str_after_split[
                    3].rstrip('0') + 'B'
        elif str_value.__contains__('Billion'):
            str_value = str_value.split(' ')[0] + 'B'
        return str_value

    def tokenize_dollars(self, tokens, i):
        """
        Function isolates the tokens that are relevant for parsing prices.
        :param tokens: Line after tokenized to tokens
        :param i: location of '$' 'Dollars' 'dollars'
        :return: same token list but after parsing prices and tokenizing it.
        """
        # for i, token in enumerate(tokens, start=j):
        token = tokens[i]
        token_str = str(tokens[i])
        if token_str == '$':     # if tokens contain sign $
            if len(tokens) > i+2 and (tokens[i+2] == 'million' or tokens[i+2] == 'billion' or tokens[i+2] == 'trillion'):
                tokens[i] = self.sub_currency_in_line((tokens[i], tokens[i+1], tokens[i+2]))         # parse $ <number> <million/billion/trillion>
                del tokens[i+1]
                del tokens[i+1]
                # self.token_index = self.token_index - 1
            elif str(tokens[i+1]).__contains__('K') or str(tokens[i+1]).__contains__('M') or str(tokens[i+1]).__contains__('B') or str(tokens[i+1]).__contains__('T'):
                tokens[i] = self.sub_currency_in_line((tokens[i], tokens[i+1]))           # parse $ <number>
                del tokens[i+1]
            else:
                tokens[i] = tokens[i+1] + ' Dollars'
                del tokens[i+1]
        elif token_str == 'Dollars' or token_str == 'dollars':        # if tokens contain word Dollars or dollars
            self.token_index = self.token_index - 2
            if i >= 3 and tokens[i-1] == 'U.S':
                self.token_index = self.token_index - 2
                new_string_to_parse = tokens[i-3]
                tokens[i-3] = self.sub_currency_in_line(('$', new_string_to_parse, tokens[i-2]))  # parse $ <number> <million/billion/trillion>
                del tokens[i]      # Removing the token Dollars/dollars
                del tokens[i-1]    # Removing the token U.S
                del tokens[i-2]    # Removing the token million/billion/trillion
            else:       # if it's "price m Dollars" or "price bn Dollars" change to $priceM  or $priceB and send to same function for parse.
                if str(tokens[i-1]).__contains__('m'):
                    substr_index = len(tokens[i-1]) - 1
                    new_string_to_parse = tokens[i-1][0:substr_index] + 'M'
                    tokens[i - 1] = self.sub_currency_in_line(('$', new_string_to_parse))
                elif str(tokens[i-1]).__contains__('bn'):
                    new_string_to_parse = tokens[i-1][0:len(tokens[i-1])-2] + 'B'
                    tokens[i - 1] = self.sub_currency_in_line(('$', new_string_to_parse))
                elif str(tokens[i-1]).__contains__('K') or str(tokens[i-1]).__contains__('M') or str(tokens[i-1]).__contains__('B') or str(tokens[i-1]).__contains__('T'):
                    tokens[i-1] = self.sub_currency_in_line(('$', tokens[i-1]))
                else:       # only <number> Dollars/dollars
                    tokens[i-1] = tokens[i-1] + ' Dollars'
                del tokens[i]
                # self.token_index = self.token_index - 1

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
            return self.sub_currency_sign_dollar(tokens)   # *** NEED TO SEND ONLY $PRICE TOKENS LIST***

    def sub_currency_sign_dollar(self, tokens):
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

    def sub_currency_k(self, first_token_str):
        """
        Functions substitutes thousands of currency to correct format for currency
        :param first_token_str: string of price in thousands: 5.1k or 42k  (with comma or without)
        :return: correct string
        """
        k_position = first_token_str.find('K')
        if first_token_str.__contains__('.'):       #If number is: 3.1K or 4.12K or 5.123K
            dot_position = first_token_str.find('.')
            if k_position - dot_position == 2:
                first_token_str = first_token_str.replace('.', ',')
                first_token_str = first_token_str.replace('K', '00')
            elif k_position - dot_position == 3:
                first_token_str = first_token_str.replace('.', ',')
                first_token_str = first_token_str.replace('K', '0')
            elif k_position - dot_position == 4:
                first_token_str = first_token_str.replace('.', ',')
                first_token_str = first_token_str.replace('K', '')
        else:                                       #If number has no comma
            first_token_str = first_token_str.replace('K', ',000')
        return first_token_str

    def sub_dates_in_line(self, tokens, i):
        """
        Functions parses the dates and replaces tokens also
        Possible states: DD M or M DD or M YYYY or DD M YYYY or DD M, YYYY
        :param tokens: list of tokens
        :param i: index of the month (January...December or JANUARY...DECEMBER) in the tokens list
        :return: haven't decided yet if to return entire list or no need or idk...
        """
        strings_to_return = list()
        month_value = self.month_dictionary.get(tokens[i])
        if len(tokens) > i+1 and tokens[i+1] == ',':                                                        #IF DATE HAS COMMA
            if len(tokens) > i+2 and len(tokens[i+2]) == 4 and self.is_number(tokens[i+2]):                 # if date contains year after coma
                if i > 0 and self.is_number(tokens[i-1]) and 0 < int(tokens[i-1]) < 32 :                    # if also day included in date
                    strings_to_return.append(month_value + '-' + tokens[i-1])   # month-day
                    strings_to_return.append(tokens[i+2] + '-' + month_value)   # year-month
                    strings_to_return.append(strings_to_return[1] + '-' + tokens[i-1])                      # year-month-day
                    tokens[i-1] = strings_to_return[0]
                    tokens[i] = strings_to_return[1]
                    tokens[i+1] = strings_to_return[2]
                    del tokens[i+2]
                    # maybe need to increment token_index by 1?
                else:                                                                                       # no day included in date
                    tokens[i] = tokens[i + 2] + '-' + month_value                               # year-month
                    del tokens[i + 1]
                    del tokens[i + 1]
            else:                                                                                           # no year included in date
                if i > 0 and self.is_number(tokens[i - 1]) and 0 < int(tokens[i - 1]) < 32:                 # if also day included in date
                    tokens[i-1] = month_value + '-' + tokens[i - 1]                             # month-day
                    del tokens[i]
                    self.token_index = self.token_index - 1
        elif len(tokens) > i+1 and len(tokens[i+1]) == 4 and self.is_number(tokens[i+1]):                   # if date contains year WITHOUT COMMA
            if i > 0 and self.is_number(tokens[i-1]) and 0 < int(tokens[i-1]) < 32:
                strings_to_return.append(month_value + '-' + tokens[i - 1])     # month-day
                strings_to_return.append(tokens[i + 1] + '-' + month_value)     # year-month
                strings_to_return.append(strings_to_return[1] + '-' + tokens[i - 1])                        # year-month-day
                tokens[i-1] = strings_to_return[0]
                tokens[i] = strings_to_return[1]
                tokens[i+1] = strings_to_return[2]
            else:                                                                                           # no day included in date
                tokens[i] = tokens[i+1] + '-' + month_value                         # year-month
                del tokens[i+1]
        elif i > 0 and self.is_number(tokens[i-1]) and 0 < int(tokens[i-1]) < 32:
                tokens[i-1] = month_value + '-' + tokens[i-1]                       # month-day
                del tokens[i]
                self.token_index = self.token_index - 1

        return strings_to_return





