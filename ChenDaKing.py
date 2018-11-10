import re
import time
import locale

class ChenDaKing:

    def __init__(self):
        self.text = 'Over 5,100 soldiers 1994 pooped 6,000 that day. They shat about 16 Thousand tons of shit every' \
                    'month in the war. Some even say 165403.66 tons.'\
                    'Some say even 12 Billion or 45 Million people used to shit the same amount that the soldiers shat.' \
                    'The exact number was 12,000,405,100. ' \
                    'Also 405 Trillion' \
                    'I have 365.24 3/4 chance to win a pen.'

        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

        self.percent_key_words = ('%', 'percent', 'percentage')
        self.dollar_key_words = ('$', 'Dollars')
        self.month_list = ('January','February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
        self.month_list_capital = ('JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER',' OCTOBER', 'NOVEMBER', 'DECEMBER')
        # self.text = '12,000,404,390 and 596 Billion'
        # print(re.findall('([1-9]\d{0,2},\d{3},\d{3},\d{3})|([1-9]\d{9,11}\.\d{1,9})|([1-9]\d{0,2}\sBillion)', self.text))

    # current_milli_time = lambda: int(round(time.time() * 1000))


    def findKeyWordsInLine(self, tokens):
        for i, token in enumerate(tokens, start=0):
            token_str = str(token)
            if token in self.percent_key_words:
                if token is 'percent' or token is 'percentage':
                    self.sub_percent_in_line((tokens[i-1], tokens[1]))
                else:
                    self.sub_percent_in_line(token)
            elif token_str in self.dollar_key_words:
                        self.tokenize_dollars(tokens)
            elif token in self.month_list or token in self.month_list_capital:
                self.sub_dates_in_line(tokens[i])
            elif token[0] is ['A-Z']:
                i = 1
            elif str(token).__contains__('-'):
                j = 2

    def sub_dates_in_line(self, tokens):
        bla = 12



    def tokenize_dollars(self, tokens):
        """
        Function isolates the tokens that are relevant for parsing prices.
        :param tokens: Line after tokenized to tokens
        :return: same token list but after parsing prices and tokenizing it.
        """
        for i, token in enumerate(tokens, start=0):
            token_str = str(token)
            if token_str[0] == '$':
                if len(tokens) > i+1 and (tokens[i+1] == 'million' or tokens[i+1] == 'billion' or tokens[i+1] == 'trillion'):
                    tokens[i] = self.sub_currency_in_line((tokens[i], tokens[i+1]))         # parse $price
                    list(tokens).remove(i+1)
                else:
                    tokens[i] = self.sub_currency_in_line(tokens[i])           # parse $price
            if token_str == 'Dollars' or token_str == 'dollars':
                if tokens[i-1] == 'U.S':

                else:
                    if str(tokens[i-1]).__contains__('m'):
                        new_string_to_parse = '$' + token[i-1][0:len(token[i-1])-2] + 'M'
                    elif str(tokens[i-1]).__contains__('bn'):
                        new_string_to_parse = '$' + token[i-1][0:len(token[i-1])-2] + 'B'
                    token[i-1] = self.sub_currency_in_line(new_string_to_parse)
                    list(tokens).remove(i)





    def sub_currency_in_line(self, tokens):
        """
        Function returns tokenized token of price with given tokens list
        :param tokens: Tokens of regarding parsing price ONLY
        :return: new token
        """
        first_token_str = str(tokens[0])
        if first_token_str.__contains__('K'):               # if price in thousands SUBSTITUTE AND RETURN CORRECT TOKEN
            if first_token_str.__contains__('$'):           # if $450K or $12.1K
                first_token_str = self.sub_currency_k(first_token_str)    # returns $450,000 or $12,100
                first_token_str.replace('$', '')
                first_token_str = first_token_str + ' Dollars'
            else:
                first_token_str = self.sub_currency_k(first_token_str)    #if 450K Dollars or 12.1K Dollars, returns 450,000 Dollars etc.
            tokens[0] = first_token_str         # Save new token.
            return tokens[0]                    # return fixed token


        if tokens[0][0] == '$':
            self.sub_currency_sign_dollar(tokens)   # *** NEED TO SEND ONLY $PRICE TOKENS LIST***



    def sub_currency_sign_dollar(self, tokens):
        token_str = str(tokens[0])
        if len(tokens) > 1:
            if tokens[1] == 'million':
                tokens[0] = token_str + 'M'
            elif tokens[1] == 'billion':
                tokens[0] = token_str + 'B'
            elif tokens[1] == 'trillion':
                tokens[0] = token_str + 'T'
            token_str = str(tokens[0])
        if len(tokens) == 1:        # $price  only
            m_position = token_str.find('M')
            b_position = token_str.find('B')
            t_position = token_str.find('T')
            dot_position = token_str.find('.')
            if m_position != -1:     # $12M or $14.5M to 12 M Dollars or 14.5 M Dollars
                token_str = token_str[1:m_position-1] + ' M Dollars'
            elif b_position != -1:   #  $15B
                if dot_position != -1:      #  $15.27B
                    dist = b_position - dot_position
                    token_str.replace('.', '')
                    if dist == 2:
                        token_str = token_str[1:b_position-1] + '00 M Dollars'
                    elif dist == 3:
                        token_str = token_str[1:b_position-1] + '0 M Dollars'
                    elif dist == 4:
                        token_str = token_str[1:b_position-1] + ' M Dollars'
                token_str = token_str[1:b_position-1] + '000 M Dollars'
            elif t_position != -1:          #  $12.7T  5T   to 12700 M Dollars and 5000000 M Dollars
                if dot_position != -1:
                    dist = t_position - dot_position
                    token_str.replace('.', '')
                    if dist == 2:
                        token_str = token_str[1:t_position-1] + '00000 M Dollars'
                    elif dist == 3:
                        token_str = token_str[1:t_position-1] + '0000 M Dollars'
                    elif dist == 4:
                        token_str = token_str[1:t_position-1] + '000 M Dollars'
                token_str = token_str[1:t_position-1] + '000000 M Dollars'
        return token_str




    def sub_currency_k(self, first_token_str):
        k_position = first_token_str.find('K')
        if first_token_str.__contains__('.'):       #If number is: 3.1K or 4.12K or 5.123K
            dot_position = first_token_str.find('.')
            if k_position - dot_position == 2:
                first_token_str.replace('.', ',')
                first_token_str.replace('K', '00')
            elif k_position - dot_position == 3:
                first_token_str.replace('.', ',')
                first_token_str.replace('K', '0')
            elif k_position - dot_position == 4:
                first_token_str.replace('.', ',')
                first_token_str.replace('K', '')
        else:                                       #If number has no comma
            first_token_str.replace('K', ',000')
        return first_token_str




    def sub_percent_in_line(self, tokens):
        #if type(tokens) is not list:
        return str(tokens[0]) + '%'         # ***CAN REMOVE CASTING????***

    def testTimes(self):
        regex_beginning = int(round(time.time() * 1000))


    def findNumbers(self):
        #First pattern of Thousands, then Millions, then Billions and finally Trillions.
        pattern = re.compile(r'(([1-9]\d{0,2},\d{3},\d{3},\d{3})|([1-9]\d{9,11}\.\d{1,9})|([1-9]\d{0,2}\sBillion))|'
                             r'(([1-9]\d{0,2},\d{3},\d{3})|([1-9]\d{6,8}\.\d{0,9})|([1-9]\d{0,2}\sMillion))|'
                             r'(([1-9]\d{0,2},\d{3})|([1-9]\d{3,5}\.\d{1,9})|([1-9]\d{0,2}\sThousand))|'
                             r'([1-9]\d{0,2}\sTrillion)|'
                             r'(\d{0,3}(.\d{0,3})?\s\d/\d)')
        self.text = pattern.sub(self.replaceNumbers, self.text)
        print(self.text)

    def replaceNumbers(self, match):
        value = match.group()
        value_str = str(value)
        if "/" in value_str:
            return value_str
        elif "Thousand" in value_str or "." in value_str:
            return self.replaceThousands(value_str)
        elif "Million" in value_str or "." in value_str:
            return self.replaceMillions(value_str)
        elif "Billion" in value_str or "." in value_str:
            return self.replaceBillions(value_str)
        elif "Trillion" in value_str or "." in value_str:
            return self.replaceTrillion(value_str)

        value_int = int(str(value).replace(',', ''))
        if value_int < 1000000:
            return self.replaceThousands(value_str)
        elif value_int < 1000000000:
            return self.replaceMillions(value_str)
        elif value_int < 1000000000000:
            return self.replaceBillions(value_str)

    def findThousands(self):
        pattern_thousands = re.compile('([1-9]\d{0,2},\d{3})|([1-9]\d{3,5}\.\d{1,9})|([1-9]\d{0,2}\sThousand)')
        self.text = pattern_thousands.sub(self.replaceThousands, self.text)
        print(self.text)

    def findMillions(self):
        pattern_millions = re.compile('([1-9]\d{0,2},\d{3},\d{3})|([1-9]\d{6,8}\.\d{0,9})|([1-9]\d{0,2}\sMillion)')
        self.text = pattern_millions.sub(self.replaceMillions, self.text)
        print(self.text)

    def findBillions(self):
        pattern_billions = re.compile(r'([1-9]\d{0,2},\d{3},\d{3},\d{3})|([1-9]\d{9,11}\.\d{1,9})|([1-9]\d{0,2}\sBillion)')
        self.text = pattern_billions.sub(self.replaceBillions, self.text)
        print(self.text)

    def findTrillions(self):
        pattern_trillions = re.compile(r'[1-9]\d{0,2}\sTrillion')
        self.text = pattern_trillions.sub(self.replaceTrillion, self.text)
        print(self.text)

    def replaceTrillion(self, value):
        # value = match.group()
        str_value = value
        str_value = str_value.split(' ')[0] + 'T'
        return str_value

    def replaceThousands(self, value):
        # value = match.group()
        str_value = value
        if "," in str_value:
            if not str_value.split(',')[1] == '000':
                str_value = str_value.split(',')[0] + '.' + str_value.split(',')[1].rstrip('0') + 'K'   #if not <int>,<int>{3}
            else:
                str_value = str_value.split(',')[0] + 'K'       #if <int>,000 when x =[1-9]
        elif str_value.__contains__("Thousand"):
            str_value = str_value.split(' ')[0] + 'K'   #if <int> Thousand
        elif str_value.__contains__("."):               #if number has no comma (,)
            comma_position = str_value.index(".")
            beginning = str_value[0:comma_position-3]
            middle = str_value[comma_position-3:comma_position]
            end = str_value[comma_position+1:]
            str_value = beginning + "." + middle + end + "K"
            # str_value = str_value.split(".")[0][:3] + "." + str_value.split(".")[0][len(str_value) - 3:] + str_value.split(".")[1] + 'K'
        return str_value

    def replaceMillions(self, value):
        # value = match.group()
        str_value = value
        if str_value.__contains__(","):
            str_after_split = str_value.split(",")
            if str_after_split[2] == '000':
                if str_after_split[1] == '000':         #If 5,000,000
                    str_value = str_after_split[0] + 'M'
                else:                                   # if 5,204,000
                    str_value = str_after_split[0] + '.' + str_after_split[1].rstrip('0') + 'M'
            else:                                       #if 5,203,400
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

    def replaceBillions(self, value):
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




obj = ChenDaKing()
obj.findNumbers()

# obj.findThousands()
# obj.findMillions()
# obj.findBillions()
# obj.findTrillions()