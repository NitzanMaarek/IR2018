# import nltk
import re
import pandas as pd
import numpy as np
import os
import locale

class RegexTest:
    def __init__(self):
        self.filePath = "C:\Users\Nitzan\Desktop\FB396001"
        self.monthList = ['January', 'February', 'March', 'April', 'June', 'July', 'September', 'October',
                          'November', 'December']
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')



    def parseAndSubNumbers(self):
        # First pattern of Thousands, then Millions, then Billions and finally Trillions.
        pattern = re.compile(r'(([1-9]\d{0,2},\d{3},\d{3},\d{3})|([1-9]\d{9,11}\.\d{1,9})|([1-9]\d{0,2}\sBillion))|'
                             r'(([1-9]\d{0,2},\d{3},\d{3})|([1-9]\d{6,8}\.\d{0,9})|([1-9]\d{0,2}\sMillion))|'
                             r'(([1-9]\d{0,2},\d{3})|([1-9]\d{3,5}\.\d{1,9})|([1-9]\d{0,2}\sThousand))|'
                             r'([1-9]\d{0,2}\sTrillion)')
        self.text = pattern.sub(self.replaceNumbers, self.text)
        print(self.text)

    def replaceNumbers(self, match):
        value = match.group()
        value_str = str(value)
        if "Thousand" in value_str or "." in value_str:
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


    def returnDates(self):
        text = open(self.filePath)
        for line in text:
            # x = re.findall(r'((?:January|February|March|April|May|June|July|August|September|'
            #                r'October|November|December)\s\d\d,\s\d{4})', line)     #matches: August 14, 2008
            #
            #
            # y = re.findall(r'\d\d\s(?:January|February|March|April|May|June|July|August|'
            #                r'September|October|November|December)\s\d{4}', line)
            #
            #
            # z = re.findall(r'\d\d\s(?:January|February|March|April|May|June|July|August|September|'
            #                r'October|November|December|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|'
            #                r'AUGUST|OCTOBER|NOVEMBER|DECEMBER)', line)


            w = re.findall(r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d\d,\s\d{4})'
                           r'|(\d\d\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4})'
                           r'|(\d\d\s(?:January|February|March|April|May|June|July|August|September|'
                           r'October|November|December|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|OCTOBER|NOVEMBER|DECEMBER))'
                           r'|((?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4})', line)
            #
            # if len(w) != 0:
            #     print(w)

            p = re.compile(r'([1-9]\d{0,2},\d{3})|([1-9]\d{3,5}\.\d{1,9})|([1-9]\d{0,2}\sThousand)') #what about 0,443
            print(type(p))
            numbersK = p.match(line)
            if numbersK is not None:
                print(numbersK)

            numbersM = re.findall(r'([1-9]\d{0,2},\d{3},\d{3})|([1-9]\d{6,8}\.\d{0,9})|([1-9]\d{0,2}\sMillion)', line) #what about 0,254,889
            # if len(numbersM) != 0:
            #     print(numbersM)

            numbersB = re.findall(r'([1-9]\d{0,2},\d{3},\d{3},\d{3})|([1-9]\d{9,11}\.\d{1-9})|([1-9]\d{0,2}Billion)', line)
            # if len(numbersB) != 0:
            #     print(numbersB)

            numbersT = re.findall(r'[1-9]\d{0,2}\sTrillion', line)


            entireRegex = re.compile('')
            # if found date
            #x = re.findall('.*?([a-zA-Z]+\s[0-9][0-9],\s[0-9][0-9][0-9][0-9]).*', line)
            # if len(y) != 0:
            #     print(y)
            # if len(x) != 0:
            #     print(x)


            #
            # if len(z) != 0:
            #     for element in z:
            #         numbers = re.findall(r'\d\d', element)
            #         month = re.findall(r'^\d', element)
            #         monthindex = self.monthList.index(month[0]) + 1
            #         print(str(monthindex) + "-" + numbers[0])

obj = RegexTest()

obj.returnDates()