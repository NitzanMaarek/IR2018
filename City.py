import json
import requests
import urllib.request
from Parser import Parser

class CityIndexer:
    """
    Indexer which helps with the cities indexing, the Indexer receives data from 2 API
    """
    def __init__(self):
        self.city_dictionary = {}       # Key = city_name, Value = state_name
        self.state_dictionary = {}      # Key = state_name, Value = state_attributes: currency, population
        self.countries = set()
        self.parser = Parser([])
        self.load_capital_cities()
        self.load_city_state_json()

    def load_capital_cities(self):
        """
        Method loads all state names, currencies and populations of capital cities
        """
        response = requests.get(r'https://restcountries.eu/rest/v2/all')
        if response.ok:
            obj = json.loads(response.content.decode('utf-8'))
            for country_dict in obj:
                state_code = country_dict['alpha2Code']
                state_name = self.lower_case_word(country_dict['name'])
                state_capital = self.lower_case_word(country_dict['capital'])
                if len(state_capital) == 0:
                    continue
                # state_capital = self.lower_case_word(state_capital) #Change city to lower case for easier comparison
                state_raw_population = country_dict['population']   # Need to parse population
                parser = Parser([])
                state_parsed_population = list((parser.create_tokens([str(state_raw_population)])).keys())[0]
                state_currencies = country_dict['currencies']  # [{'code': NIS, 'name': 'New Israeli Shekels', 'symbol': ''}]
                self.city_dictionary[state_capital] = state_name
                currency_dir = state_currencies[0]
                currencies_list = [''.join(['Currency: ', ': ', currency_dir['name']])]
                self.state_dictionary[state_name] = ' '.join([state_name] + currencies_list + [state_parsed_population])

    def load_city_state_json(self):
        """
        Method adds to dictionary all cities from the cities API
        """
        with urllib.request.urlopen('https://raw.githubusercontent.com/russ666/all-countries-and-cities-json/'
                                    '6ee538beca8914133259b401ba47a550313e8984/countries.json') as url:
            data = json.loads(url.read().decode())
            for state in data:
                for city in data[state]:
                    city = self.lower_case_word(city)
                    if city not in self.city_dictionary:
                        self.city_dictionary[city] = state


    def get_city_attributes(self, city_name):
        """
        Method returns attributes with given city.
        :param city_name:
        :return: city attributes as a list
        """
        if city_name is not None:
            city_name = self.lower_case_word(city_name)
            if city_name in self.city_dictionary:
                state = self.lower_case_word(self.city_dictionary[city_name])
                if state == 'united states' or state == 'usa':
                    state = 'united states of america'
                elif state == 'russia':
                    state = 'russian federation'
                elif state == 'bolivia':
                    state = 'bolivia (plurinational state of)'
                elif state == 'united kingdom':
                    state = 'united kingdom of great britain and northern ireland'
                elif state == 'iran':
                    state = 'iran (islamic republic of)'
                elif state == 'venezuela':
                    state = 'venezuela (bolivarian republic of)'
                elif state == 'republic of moldova':
                    state = 'moldova (republic of)'
                if state in self.state_dictionary:
                    if not state in self.countries:
                        self.countries.add(state)
                    return self.state_dictionary[state]
                else:
                    return None
        return None

    def lower_case_word(self, token):
        """
        Method checks if token is an alphabetical word. If so make it lower case
        :param token: string
        :return: if word: then same word in lower case, otherwise same token
        """
        chars_list = []    #list of strings to join after.
        if token is not None:
            for i, char in enumerate(token, start=0):
                char_int_rep = ord(char)
                if 65 <= char_int_rep <= 90:     #if char is UPPER case, make it lower case
                    chars_list.append(chr(char_int_rep + 32))
                else:
                    chars_list.append(char)

            token = ''.join(chars_list)
        return token

class CityToken:
    """
    City object that represents a city we encounter in one of the document's tags
    """
    def __init__(self, city_name = None, disk_string = None, attr = []):
        self.city_name = city_name
        self.df = 0
        self.attr = attr
        self.doc_dict = {}

    def add_data(self, doc_pointer, doc_num):
        """
        Adding data from a document to the city
        :param doc_num: document ID
        :param doc_pointer: document pointer
        :param list: list of parameter regarding the token from the document
        """
        self.df += 1
        self.doc_dict[doc_num] = doc_pointer

    def string_to_disk(self):
        """
        Converting a token object to string for writing to the disk without the pointers to the posting files
        :return: string with all the city's parameters
        """
        params = []
        params.append(str(self.city_name))
        params.append(str(self.df))
        for item in self.attr:
            params.append(item)

        for k, v in self.doc_dict:
            params.append(k + ' ' + v + ',')

        return ' '.join(params)

    def create_string_from_doc_dictionary(self):
        """
        Creates a string with all the parameters o the documents that are in the city's dictionary
        :return: String with all the parameters
        """
        dict_str = ''
        doc_strings = []
        if hasattr(self, 'attr'):
            for item in self.attr:
                doc_strings.append(item)
        for doc_id in self.doc_dict:
            doc_strings.append(''.join(['< ', doc_id, ' ', str(self.doc_dict[doc_id]), ' >', ' ']))
        doc_strings.append('\n')
        return ''.join(doc_strings)

    def merge_tokens(self, second_city):
        """
        Merging two city tokens, used when we encounter two tokens with the same name from different batches
        and we want to make them into one city token.
        :param second_city: Second city token to merge into the first one
        """
        self.df += second_city.df
        self.doc_dict = {**self.doc_dict, **second_city.doc_dict}

    def set_attr(self, attr):
        """
        Setting the attributes given to the city by the City Indexer
        :param attr: list of attributes
        """
        self.attr = attr