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
            x = re.findall(r'((?:January|February|March|April|May|June|July|August|September|'
                           r'October|November|December)\s\d\d,\s\d{4})', line)     #matches: August 14, 2008

            # y = re.findall('.*[0-9][0-9]\s(January|February|March|April|May|June|July|August|September|'
            #                'October|November|December|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|'
            #                'OCTOBER|NOVEMBER|DECEMBER).*', line)
            y = re.findall(r'\d\d\s(?:January|February|March|April|May|June|July|August|'
                           r'September|October|November|December)\s\d{4}', line)

            z = re.findall(r'\d\d\s(?:January|February|March|April|May|June|July|August|September|'
                           r'October|November|December|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|'
                           r'AUGUST|OCTOBER|NOVEMBER|DECEMBER)', line)
            # if found date
            #x = re.findall('.*?([a-zA-Z]+\s[0-9][0-9],\s[0-9][0-9][0-9][0-9]).*', line)
            # if len(y) != 0:
            #     print(y)
            # if len(x) != 0:
            #     print(x)
            if len(z) != 0:
                for element in z:
                    numbers = re.findall(r'\d\d', element)
                    month = re.findall(r'^\d', element)
                    monthindex = self.monthList.index(month[0]) + 1
                    print(str(monthindex) + "-" + numbers[0])
