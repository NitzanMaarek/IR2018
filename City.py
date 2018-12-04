import json
import requests
import urllib.request
from Parser import Parser

class CityIndexer:
    def __init__(self):
        self.city_dictionary = {}       # Key = city_name, Value = state_name
        self.state_dictionary = {}      # Key = state_name, Value = state_attributes: currency, population
        self.inverted_index = {}
        self.parser = Parser([])
        self.load_capital_cities()
        self.load_city_state_json()

    def load_capital_cities(self):
        """
        Method loads all state names, currencies and populations of capital cities
        :return:
        """
        response = requests.get(r'https://restcountries.eu/rest/v2/all')
        if response.ok:
            obj = json.loads(response.content.decode('utf-8'))
            for country_dict in obj:
                state_code = country_dict['alpha2Code']
                state_name = country_dict['name']
                state_capital = country_dict['capital']
                state_raw_population = country_dict['population']   # Need to parse population
                state_parsed_population = list((self.parser.create_tokens([str(state_raw_population)])).keys())[0]
                state_currencies = country_dict['currencies']  # [{'code': NIS, 'name': 'New Israeli Shekels', 'symbol': ''}]
                self.city_dictionary[state_capital] = state_code
                currencies_list = []
                for state_currency in state_currencies:
                    for k, v in state_currency.items():
                        currency_list = []
                        if not v is None:
                            currency_list.append(k + ': ' + v)
                    currencies_list.append(' '.join(currency_list))
                # currencies_list = [k + ': ' + v for k, v in state_currencies[0].items()]
                self.state_dictionary[state_code] = ' '.join([state_name] + currencies_list + [state_parsed_population])

    def load_city_state_json(self):
        """
        Method adds to dictionary all cities:
        :return:
        """
        with urllib.request.urlopen('https://raw.githubusercontent.com/russ666/all-countries-and-cities-json/'
                                    '6ee538beca8914133259b401ba47a550313e8984/countries.json') as url:
            data = json.loads(url.read().decode())
            for state in data:
                for city in data[state]:
                    if not city in self.city_dictionary:
                        self.city_dictionary[city] = state



    def get_city_attributes(self, city_name):
        """
        Method returns attributes with given city.
        :param city_name:
        :return:
        """
        if city_name in self.city_dictionary:
            return self.state_dictionary[self.city_dictionary[city_name]]
        return None

class CityToken:
    def __init__(self, city_name = None, disk_string = None, attr = []):
        self.city_name = city_name
        self.df = 0
        self.attr = attr
        self.doc_dict = {}

    def add_data(self, doc_pointer, doc_num):
        self.df += 1
        self.doc_dict[doc_num] = doc_pointer

    def string_to_disk(self):
        """
        Converting a token object to string for writing to the disk without the pointers to the posting files
        :return:
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
        dict_str = ''
        doc_strings = []
        if hasattr(self, 'attr'):
            for item in self.attr:
                doc_strings.append(item)
        for doc_id in self.doc_dict:
            doc_strings.append(''.join(['<', doc_id, ' ', str(self.doc_dict[doc_id]), '>', ' ']))
        doc_strings.append('\n')
        return ' '.join(doc_strings)

    def merge_tokens(self, second_city):
        self.df += second_city.df
        self.doc_dict = {**self.doc_dict, **second_city.doc_dict}