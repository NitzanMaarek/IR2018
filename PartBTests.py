from Searcher import Searcher
import Indexer
import os
import pandas as pd
from Parser import Parser
import Main
from sklearn.model_selection import RandomizedSearchCV

main_dir = r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\test directory\created files'
corpus_path = r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\test directory\10 files'
terms_dict = Indexer.load_obj(main_dir,'main terms dictionary', directory='')
city_dictionary = Indexer.load_obj(main_dir,'cities dictionary', directory='cities')

stop_words_list = Main.read_stop_words_lines(corpus_path)
query = 'British Channel impact'

query_parser = Parser(stop_words_list)
parsed_query = list(query_parser.parser_pipeline([query], stem=False).keys())
query_parser.erase_dictionary()

relevant = ' - projected and actual impact on the life styles of the British ' \
           ' Long term changes to economic policy and relations major changes' \
           ' to other transportation systems linked with the Continent'
relevant_parsed = list(query_parser.parser_pipeline([relevant], stem=False).keys())
query_parser.erase_dictionary()

not_relevant = ' - expense and construction schedule routine marketing ploys by ' \
               'other channel crosses (i.e.,schedule changes, price drops, etc.)'
not_relevant_parsed = list(query_parser.parser_pipeline([not_relevant], stem=False).keys())

searcher = Searcher(corpus_path, main_dir, terms_dict, city_dictionary, 'doc2vec.model', 'doc tags')

query_results = searcher.search(parsed_query, relevant_parsed, not_relevant_parsed, x=1000)

print('Number of documents returned: ' + str(len(query_results)))
print(query_results)

df = pd.read_csv(r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\treceval\qrels.txt', sep=' ',
                 names=['query id', 'maybe result', 'file id', 'result'])

query_id = 352
df = df[(df['query id'] == query_id) & (df['result'] == 1)]
# df = df[df['query id'] == query_id]

sorted_query_results = sorted(query_results.items(), key=lambda kv: kv[1], reverse=True)
doc_count = 0
i = 0
rank = 1
place = 1
doc_list = list(df['file id'])
lines = []
for doc_tuple in sorted_query_results:
    if rank == 0:
        print(doc_tuple[0])
    line = str(query_id) + ' 0 ' + str(doc_tuple[0]) + ' ' + str(rank) + ' ' + str(doc_tuple[1]) + ' 0 \n'
    rank += 1
    lines.append(line)
    if doc_tuple[0] in doc_list:
        doc_count += 1
        print(str(place) + ': ' + str(rank))
        place += 1
        # print(doc_tuple[0])
    i += 1

print('result = ' + str(doc_count) + '/' + str(len(query_results)))
with open('results.txt', 'w') as f:
    f.writelines(lines)