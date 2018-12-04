import json
import requests
import urllib.request
from Parser import Parser

class City:
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
                state_parsed_population = (self.parser.create_tokens([state_raw_population])).keys()[0]
                state_currencies = country_dict['currencies']  # [{'code': NIS, 'name': 'New Israeli Shekels', 'symbol': ''}]
                self.city_dictionary[state_capital] = state_code
                self.state_dictionary[state_code] = ''.join([state_name, ' ', state_currencies, ' ', state_parsed_population,' '])

    def load_city_state_json(self):
        """
        Method adds to dictionary all cities:
        :return:
        """
        with urllib.request.urlopen('https://raw.githubusercontent.com/russ666/all-countries-and-cities-json/6ee538beca8914133259b401ba47a550313e8984/countries.json') as url:
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


    # def get_city_attributes(self, city_name):
    #     if city_name is None or len(city_name) == 0:
    #         return None
    #     if city_name in self.city_dictionary:
    #         return self.city_dictionary[city_name]
    #     else:
    #         response = requests.get(r'https://restcountries.eu/rest/v2/capital/' + city_name)
    #         if response.ok:     # If connection to API server succeeded.
    #             self.add_city_to_dictionary(response, city_name)

    def add_city_to_dictionary(self, city_name):
        if not city_name in self.city_dictionary:
            response = requests.get(r'https://restcountries.eu/rest/v2/capital/' + city_name)
            if response.ok:
                obj = json.loads(response.content.decode('utf-8'))[0]
                state = ''.join(['State: ', str(obj['name'])])
                currencies = ''.join(['Currencies: '] + [d['name'] for d in obj['currencies']])
                population_size = obj['population']
                # pop = list(self.parser.create_tokens([population_size]).keys())
                # parsed_population = list(self.parser.create_tokens([population_size]).keys())[0]
                population = ''.join(['Population: ', str(population_size)])
                self.city_dictionary[city_name] = ''.join([state, ' ', currencies, ' ', population])