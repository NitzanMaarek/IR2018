# import nltk
import re
import pandas as pd
import numpy as np
import os

class RegexTest:
    def __init__(self):
        self.filePath = "C:\Users\Nitzan\Desktop\FB396001"
        self.monthList = ['January', 'February', 'March', 'April', 'June', 'July', 'September', 'October',
                          'November', 'December']

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

            numbersK = re.findall(r'([1-9]\d{0,2},\d{3})|([1-9]\d{3,5}\.\d{1,9})|([1-9]\d{0,2}\sThousand)', line) #what about 0,443
            # if len(numbersK) != 0:
            #     print(numbersK)

            numbersM = re.findall(r'([1-9]\d{0,2},\d{3},\d{3})|([1-9]\d{6,8}\.\d{0,9})|([1-9]\d{0,2}\sMillion)', line) #what about 0,254,889
            # if len(numbersM) != 0:
            #     print(numbersM)

            numbersB = re.findall(r'([1-9]\d{0,2},\d{3},\d{3},\d{3})|([1-9]\d{9,11}\.\d{1-9})|([1-9]\d{0,2}Billion)', line)
            if len(numbersB) != 0:
                print(numbersB)

            numbersT = re.findall(r'[1-9]\d{0,2}\sTrillion', line)

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
