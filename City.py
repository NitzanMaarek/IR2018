import json
import requests
from Parser import Parser

class City:
    def __init__(self):
        self.city_dictionary = {}
        self.inverted_index = {}
        self.parser = Parser([])

    def get_city_attributes(self, city_name):
        if city_name is None or len(city_name) == 0:
            return None
        if city_name in self.city_dictionary:
            return self.city_dictionary[city_name]
        else:
            response = requests.get(r'https://restcountries.eu/rest/v2/capital/' + city_name)
            if response.ok:     # If connection to API server succeeded.
                self.add_city_to_dictionary(response, city_name)

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