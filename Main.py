from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import datetime
import os
import multiprocessing as mp
from tkinter.ttk import Treeview

import Indexer
from ReadFile import ReadFile
import Preferences
import shutil
from Parser import Parser
import csv

class GUI:
    """
    Class is in charge of showcasing the GUI and managing the GUI logic.
    """

    def __init__(self):
        """
        Initializes root window, frames, labels, entries, buttons
        """
        self.term_dictionary = {}
        # self.searcher = Searcher()

        self.root = Tk()
        self.root.title('IR2018')
        self.root.geometry('610x293')
        self.top_frame = Frame(self.root)
        self.top_frame.pack(side=TOP)
        self.bottom_frame = Frame(self.root)
        self.bottom_frame.pack(side=BOTTOM)

        # *** Labels ***
        self.corpus_stopwords_label = Label(self.top_frame, text='Corpus and stop-words path:')
        self.dictionary_posting_label = Label(self.top_frame, text='Dictionary and Posting path:')
        self.language_label = Label(self.top_frame, text='Language:')
        self.result1_label = Label(self.top_frame, text='Number of documents indexed:')
        self.result2_label = Label(self.top_frame, text='Number of unique terms found in Corpus:')
        self.result3_label = Label(self.top_frame, text='Total runtime (in seconds):')
        self.single_query_label = Label(self.bottom_frame, text='Single query:')
        self.query_file_label = Label(self.bottom_frame, text='Query file:')
        self.city_selection_label = Label(self.bottom_frame, text='City selection:')

        # *** Entries - text boxes ***
        self.corpus_stopwords_entry = Entry(self.top_frame, width=50)
        self.dictionary_posting_entry = Entry(self.top_frame, width=50)
        self.result1_entry = Entry(self.top_frame)
        self.result2_entry = Entry(self.top_frame)
        self.result3_entry = Entry(self.top_frame)
        self.single_query_entry = Entry(self.bottom_frame, width=33)
        self.query_file_entry = Entry(self.bottom_frame, width=33)
        self.city_selection_entry = Entry(self.bottom_frame, width=33)


        # *** Stem checkbox ***
        self.stem_flag = IntVar()  # 0 = unchecked,   1 = checked
        self.stem_checkbox = Checkbutton(self.top_frame, text="Use stem", variable=self.stem_flag)

        # *** Semantics checkboxes ***
        self.semantics_flag = IntVar()
        self.semantics_checkbox = Checkbutton(self.bottom_frame, text='Use Semantics', variable=self.semantics_flag)

        # *** Buttons ***
        self.activate_button = Button(self.bottom_frame, text='Activate', height=2, width=8, command=self.activate_button_clicked)
        self.reset_button = Button(self.bottom_frame, text='Reset', height=2, width=8, command=self.reset_button_clicked)
        self.view_dict_button = Button(self.bottom_frame, text='View\nDictionary', width=8, command=self.view_dictionary_button_clicked)
        self.load_dict_button = Button(self.bottom_frame, text='Load\nDictionary', width=8, command=self.load_dictionary_button_clicked)
        self.browse_corpus_button = Button(self.top_frame, text='Browse', command=self.browse_stop_words_corpus)
        self.browse_destination_file_button = Button(self.top_frame, text='Browse', command=self.browse_destination_files)
        self.run_single_query_button = Button(self.bottom_frame, text='Run', command=self.run_single_query_button_clicked)
        self.run_query_file_button = Button(self.bottom_frame, text='Run', command=self.run_query_file_button_clicked)
        self.browse_query_file_button = Button(self.bottom_frame, text='Browse', command=self.browse_query_file_button_clicked)

        # *** Status bar ***

        # *** Language drop-down menu ***
        self.variable = StringVar(self.root)
        self.variable.set("Select language")  # default value
        self.drop_down_menu = OptionMenu(self.top_frame, self.variable, '<None>')
        self.drop_down_menu.grid(row=2, column=1, sticky=W, pady=4)

        # *** City drop-down menu ***
        self.city_variable = StringVar(self.root)
        self.city_variable.set("Select City")
        self.city_drop_down_menu = OptionMenu(self.bottom_frame, self.city_variable, '<None>', command=self.update_city_selection_entry)
        self.city_drop_down_menu.grid(row=3, column=2, padx=1)

        # *** using grid ***
        self.corpus_stopwords_label.grid(row=0, column=0, sticky=E)
        self.corpus_stopwords_entry.grid(row=0, column=1)

        self.dictionary_posting_label.grid(row=1, column=0, sticky=E)
        self.dictionary_posting_entry.grid(row=1, column=1)

        self.browse_corpus_button.grid(row=0, column=3, sticky=W, padx=4)
        self.browse_destination_file_button.grid(row=1, column=3, sticky=W, padx=4)

        self.language_label.grid(row=2, column=0, sticky=E)

        self.stem_checkbox.grid(row=2, column=3, sticky=E)

        self.result1_label.grid(row=4, column=0, sticky=E)
        self.result1_entry.grid(row=4, column=1, sticky=W)
        # self.result1_entry.config(state=DISABLED)

        self.result2_label.grid(row=5, column=0, sticky=E)
        self.result2_entry.grid(row=5, column=1, sticky=W)
        # self.result2_entry.config(state=DISABLED)

        self.result3_label.grid(row=6, column=0, sticky=E)
        self.result3_entry.grid(row=6, column=1, sticky=W)
        # self.result3_entry.config(state=DISABLED)

        # Bottom frame
        self.activate_button.grid(row=0, column=1, sticky=W)
        self.reset_button.grid(row=0, column=1)
        self.view_dict_button.grid(row=0, column=1, sticky=E)
        self.load_dict_button.grid(row=0, column=2, sticky=W, padx=3, pady=4)

        self.single_query_label.grid(row=1, column=0, sticky=E)
        self.single_query_entry.grid(row=1,column=1)
        self.run_single_query_button.grid(row=1,column=2, sticky=W, padx=4, pady=2)

        self.query_file_label.grid(row=2, column=0, sticky=E)
        self.query_file_entry.grid(row=2, column=1)
        self.run_query_file_button.grid(row=2, column=2, sticky=W, padx=4)
        self.browse_query_file_button.grid(row=2, column=2, ipadx=8, sticky=E)
        # TODO: Fix layout of buttons

        self.city_selection_label.grid(row=3, column=0, sticky=E)
        self.city_selection_entry.grid(row=3, column=1)

        self.semantics_checkbox.grid(row=2, column=3, sticky=W, padx=2)

        self.root.mainloop()

    # def gui_pipeline(self):

    def check_paths(self, path, dir_name):
        """
        Method checks if path exists for dir_name, if not then show an error message
        :param path: string of path
        :param dir_name: string of entry
        :return: True if path is good, False otherwise
        """
        if path is None or path == '':
            messagebox.showerror('Error Message', 'Field ' + dir_name + ' is empty.')
            return False
        if not os.path.exists(path):
            messagebox.showerror('Error Message', 'Path in ' + dir_name + ' field does not exist.')
            return False
        return True


    def activate_button_clicked(self):
        """
        Method activates operation on given paths if they exist, otherwise nothing happens
        Calculates number of docs indexed, number of unique terms in corpus and total runtime and updates entries accordingly
        """
        corpus_path = self.corpus_stopwords_entry.get()
        output_path = self.dictionary_posting_entry.get()
        if self.check_paths(corpus_path, 'Corpus and stop-words'):
            if self.check_paths(output_path, 'Dictionary and Posting'):
                # activate readfile with both paths.
                output_path = output_path + '\\'
                self.main_dir = output_path
                # Preferences.stem = bool(self.stem_flag.get())
                restart_files(output_path)
                start_time = datetime.datetime.now()
                if self.stem_flag.get() == 1:
                    self.stem = True
                else:
                    self.stem = False
                total_docs, length_of_terms_dictionary = read_directory(main_dir=output_path, directory=corpus_path, multiprocess=parallel, batch_size=20000, stem=self.stem)
                finish_time = datetime.datetime.now()
                messagebox.showinfo("Activation Finished", 'Activation finished successfully')
                self.result1_entry.delete(0,END)
                self.result1_entry.insert(INSERT, str(total_docs))
                self.result2_entry.delete(0, END)
                self.result2_entry.insert(INSERT, str(length_of_terms_dictionary))
                self.result3_entry.delete(0, END)
                self.result3_entry.insert(INSERT, (finish_time-start_time).total_seconds())
                languages = list(Indexer.load_obj(self.main_dir, name='languages', directory=''))
                self.update_option_menu(languages)

    def reset_button_clicked(self):
        """
        Method deletes all posting files and dictionary. Also cleans main memory.
        """
        output_path = self.dictionary_posting_entry.get() + '\\'
        if self.check_paths(output_path, 'Dictionary and Posting'):
            # self.delete_files_in_directory()
            remove_files(output_path)
            self.term_dictionary.clear()
            messagebox.showinfo("Reset Results", 'Posting and dictionary files have been deleted successfully')


    def view_dictionary_button_clicked(self):
        """
        Method opens a window with dictionary in it.
        """

        # self.display_treeview_dictionary()
        # TODO: Need to check if need to show dictionary of stemming or not.

        if len(self.term_dictionary) != 0:
            # self.display_dictionary()
            self.display_treeview_dictionary()

        else:
            messagebox.showerror('Error Message', 'No dictionary to show.\nPlease load dictionary to memory first.')


    #
    # def display_dictionary(self):
    #     """
    #     Method opens a new window with the dictionary in it: displaying terms and their total frequency in text.
    #     """
    #     window = Toplevel(self.root)
    #     window.geometry('500x500')
    #     # window.title = 'Dictionary'
    #     scrollbar = Scrollbar(window)
    #     scrollbar.pack(side=RIGHT, fill=Y)
    #     listbox = Listbox(window)
    #     listbox.size()
    #     listbox.pack(fill="both", expand=TRUE)
    #
    #     for key in self.term_dictionary.keys():
    #         listbox.insert(END, key)
    #
    #     listbox.config(yscrollcommand=scrollbar.set)
    #     scrollbar.config(command=listbox.yview)

    def display_search_results(self):
        """
        Method opens a new window with the search results
        """
        window = Toplevel(self.root)
        window.geometry('500x500')
        top_frame = Frame(window)
        bottom_frame = Frame(window)
        self.search_results_tree_view = Treeview(window)
        self.search_results_tree_view['columns'] = ('Query ID', 'Document ID')
        self.search_results_tree_view.heading('Query ID', text='Query ID')
        self.search_results_tree_view.column('Query ID', anchor='w', width=150)
        self.search_results_tree_view.heading('Document ID', text='Document ID')
        self.search_results_tree_view.column('Document ID', anchor='center', width=150)
        self.search_results_tree_view.pack(side=LEFT, fill='both', expand=TRUE)
        self.search_results_scroll_bar = Scrollbar(bottom_frame)
        self.search_results_scroll_bar.pack(side=RIGHT, fill=Y)

        self.search_results_tree_view.configure(yscrollcommand=self.search_results_scroll_bar.set)
        self.search_results_scroll_bar.config(command=self.search_results_tree_view.yview)
        # TODO: Handle results
        # self.insert_search_results_to_table(results)

        self.save_results_button = Button(top_frame, text='Save Results', command=self.browse_save_results)

    def browse_save_results(self, ):
        """
        Method opens a browse window to save the query results in trec eval format
        Trec eval format: query_id, iter=0, doc_no, rank, similarity, run_id=mt
        """


    def display_treeview_dictionary(self):
        """
        Method initializes a table of contents to show terms dictionary
        """
        window = Toplevel(self.root)
        window.geometry('500x500')
        self.tree_view = Treeview(window)
        self.tree_view['columns'] = ('Term', 'df', 'Pointer', 'Total freq.')
        self.tree_view.heading("#0", text='Index', anchor='center')
        self.tree_view.column("#0", anchor='w', width=70)
        self.tree_view.heading('Term', text='Term')
        self.tree_view.column('Term', anchor='w', width=150)
        self.tree_view.heading('df', text='df')
        self.tree_view.column('df', anchor='center', width=50)
        self.tree_view.heading('Pointer', text='Pointer')
        self.tree_view.column('Pointer', anchor='center', width=100)
        self.tree_view.heading('Total freq.', text='Total freq.')
        self.tree_view.column('Total freq.', anchor='center', width=50)
        # self.tree_view.bind("<ButtonRelease-1>", self.show_enteties)
        self.tree_view.pack(side=LEFT, fill='both', expand=TRUE)

        self.scrollbar = Scrollbar(window)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.tree_view.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.tree_view.yview)

        self.insert_dictionary_to_table()

    def show_entities(self):
        current_doc = self.tree_view.focus()
        print(current_doc)

    def insert_dictionary_to_table(self):
        """
        Method inserts the dictionary fields into the table
        Dictionary: Key = term, Value = list of: df, total_tf, pointer to posting
        """
        for i, term in enumerate(self.term_dictionary.keys(), start=0):
            term_attributes = self.term_dictionary[term]
            # term_attributes: [pointer, df, total freq.]
            self.tree_view.insert('', 'end', text=i, values=[term, term_attributes[1], term_attributes[0],  term_attributes[2]])

    def load_dictionary_button_clicked(self):
        """
        Method loads dictionary to memory.
        """
        if self.check_paths(self.dictionary_posting_entry.get(), 'Dictionary and Posting'):
            self.main_dir = self.dictionary_posting_entry.get()
            if bool(self.stem_flag.get()):
                self.term_dictionary = Indexer.load_obj(self.main_dir, 'stem main terms dictionary', '')
            else:
                self.term_dictionary = Indexer.load_obj(self.main_dir, 'main terms dictionary', '')
            messagebox.showinfo("Load successful", 'Dictionary loaded.')

    def update_option_menu(self, language_list):
        """
        Method updates scroll-down menu of languages with strings in a given list.
        :param alist: list of strings (=languages)
        """
        menu = self.drop_down_menu["menu"]
        menu.delete(0, "end")
        for string in language_list:
            menu.add_command(label=string, command=lambda value=string: self.variable.set(value))

    def browse_stop_words_corpus(self):
        """
        Method called when the browse button for corpus and stopwords was clicked.
        Creates a browse window for directories only!
        Adds path as text to entry.
        """
        curr_directory = os.getcwd()
        dir_name = filedialog.askdirectory(initialdir=curr_directory, title="Select a directory")
        if len(dir_name) > 0:
            self.corpus_stopwords_entry.delete(0, END)
            self.corpus_stopwords_entry.insert(INSERT, dir_name)

    def browse_destination_files(self):
        """
        Method called when the browse button for destination files was clicked.
        Creates a browse window for directories only!
        Adds path as text to entry.
        """
        curr_directory = os.getcwd()
        dir_name = filedialog.askdirectory(initialdir=curr_directory, title="Select a directory")
        if len(dir_name) > 0:
            self.dictionary_posting_entry.delete(0, END)
            self.dictionary_posting_entry.insert(INSERT, dir_name)

    # def display_dictionary(self):

    def run_single_query_button_clicked(self):
        """
        Method takes string in entry and passes it to Searcher.
        Pops up window with results returned from Searcher
        """
        postings_directory = self.dictionary_posting_entry.get()
        stopwords_directory = self.corpus_stopwords_entry.get()
        single_query = self.single_query_entry.get()
        if single_query is None:
            messagebox.showerror('Error Message',
                                 'Cannot retrieve documents without a query.\nPlease insert a query in field "Single query".')
            return
        if postings_directory is None:
            messagebox.showerror('Error Message', 'Cannot retrieve documents without dictionary and posting files path.\nPlease insert path of dictionary and posting files.')
            return
        if stopwords_directory is None:
            messagebox.showerror('Error Message', 'Cannot retrieve documents without corpus and stop-words files path.\nPlease insert path of corpus and stop-words file.')
            return
        if self.stem_flag.get() == 1:
            stem_warning_result = messagebox.askquestion('Stemming confirmation', 'Are you sure you want to use stemming?')
            if stem_warning_result == 'yes':
                self.stem = True
            else:
                self.stem = False
        # result = list of results that needs to be shown to user
        # result = searcher.pipeline(stopwords_directory, postings_directory, single_query, self.stem, bool(self.semantics_flag.get()))
        # TODO: Handle results to show according to trecval.

    def run_query_file_button_clicked(self):
        """
        Method takes text from file and converts to list of strings, each string is query
        Passes list to Searcher
        Pops up window with results returned from Searcher
        """
        postings_directory = self.dictionary_posting_entry.get()
        stopwords_directory = self.corpus_stopwords_entry.get()
        query_file = self.query_file_entry.get()
        if query_file is None:
            messagebox.showerror('Error Message',
                                 'Cannot retrieve documents without a query file.\nPlease insert a query file in field "Query file".')
            return
        if not os.path.exists(query_file):
            messagebox.showerror('Error Message', 'Query file does not exist.')
        if postings_directory is None:
            messagebox.showerror('Error Message',
                                 'Cannot retrieve documents without dictionary and posting files path.\nPlease insert path of dictionary and posting files.')
            return
        if stopwords_directory is None:
            messagebox.showerror('Error Message',
                                 'Cannot retrieve documents without corpus and stop-words files path.\nPlease insert path of corpus and stop-words file.')
            return
        if self.stem_flag.get() == 1:
            stem_warning_result = messagebox.askquestion('Stemming confirmation',
                                                         'Are you sure you want to use stemming?')
            if stem_warning_result == 'yes':
                self.stem = True
            else:
                self.stem = False

        query_file_content = ''
        with open(query_file, 'r') as f:
            query_file_content = f.readlines()


        # result = list of results that needs to be shown to user
        # result = searcher.pipeline(stopwords_directory, postings_directory, query_file_content, self.stem, bool(self.semantics_flag.get()))
        # TODO: Handle results to show according to trec eval.

    def browse_query_file_button_clicked(self):
        """
        Method opens browse window for query file selection.
        Adds path of file to entry.
        """
        # project_directory = os.getcwd()
        query_file = filedialog.askopenfile(parent=self.root, mode='rb', title='Choose a file')
        if query_file is not None:
            self.query_file_entry.delete(0,END)
            self.query_file_entry.insert(INSERT, query_file.name)

    def update_city_selection_entry(self, city):
        """
        Method gets city from city option menu
        And updates the city entry list
        :param city: city in option menu
        """
        cities_in_entry = self.city_selection_entry.get()
        if len(cities_in_entry) == 0:
            cities_in_entry = city + ', '
        else:
            cities_in_entry = cities_in_entry + city + ', '
        self.city_selection_entry.delete(0,END)
        self.city_selection_entry.insert(INSERT, cities_in_entry)

    def update_city_selection_list(self, list):
        """
        Method updates the list of cities option menu with given list
        :param list:
        :return:
        """
        # TODO: Need to have city list prepared in advance from corpus given.
        # TODO: Need to add to active_button_clicked() extraction of cities in corpus and update the city option menu.

    def insert_search_results_to_table(self, results):
        """
        Method inserts search results to results view table
        :param results: Dictionary: Key = query id, Value = List[doc nums,...,..]
        """
        for query in results:
            documents = results[query]
            for document in documents:
                self.search_results_tree_view.insert('', 'end', text=query, values=[document])
        # TODO: Debug insertion

def read_directory(main_dir, directory, multiprocess, batch_size=20000, stem=False):
    """
    Iterating over files in a directory and opening ReadFile object for each one.
    The ReadFile object processes the file and creates Document objects.
    After finishing a certain amount of Documents the function writes the data to the disk.
    :param directory: directory to read path
    :param multiprocess: multiprocess or sequential
    :param batch_size: after how many files write the data to the disk
    """
    jobs = []
    file_count = 0
    total_doc_count = 0
    next_batch_num = 0
    language_set = set()

    stop_words_list = read_stop_words_lines(directory)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file == 'stop_words.txt':
                path = os.path.join(root, file)
                if multiprocess:
                    job = pool.apply_async(ReadFile, (file, q, path, stop_words_list, stem))
                    jobs.append(job)
                    file_count += 1
                    if file_count == 300:
                        processed_docs, next_batch_num, partial_language_set = dump_proceesed_docs_to_disk(main_dir, jobs, batch_size, next_batch_num, stem)
                        language_set = language_set.union(partial_language_set)
                        next_batch_num += 1
                        total_doc_count += processed_docs
                        jobs = []
                        file_count = 0
                else:
                    ReadFile(file, q, path, stop_words_list, stem)


    if len(jobs) > 0:
        processed_docs, next_batch_num, partial_language_set = dump_proceesed_docs_to_disk(main_dir, jobs, batch_size, next_batch_num, stem)
        language_set = language_set.union(partial_language_set)
        total_doc_count += processed_docs

    # with open(main_dir + 'languages list.csv', 'w') as cities_file:
    #     wr = csv.writer(cities_file, quoting=csv.QUOTE_ALL)
    #     wr.writerow(list(language_set))
    #     # cities_file.writelines()

    Indexer.save_obj(main_dir, language_set, name='languages', directory='')

    cities_posting = pool.apply_async(Indexer.create_cities_posting, (main_dir, False, ))

    # print('total docs: ' + str(total_doc_count))
    # print('Until merge runtime: ' + str(datetime.datetime.now() - start_time))

    merge_pickles_to_terms_dictionary(main_dir, stem=stem)
    # print('Until saving dictionary by prefixes: ' + str(datetime.datetime.now() - start_time))

    terms_dictionary = merge_tokens_dictionary(main_dir)
    # print('Until saving dictionary as one file: ' + str(datetime.datetime.now() - start_time))

    # print('Trying to save and load dictionary')
    if stem:
        Indexer.save_obj(main_dir, obj=terms_dictionary, name='stem main terms dictionary', directory='')
    else:
        Indexer.save_obj(main_dir, obj=terms_dictionary, name='main terms dictionary', directory='')
    if stem:
        term_dict = Indexer.load_obj(main_dir, name='stem main terms dictionary', directory='')
    else:
        term_dict = Indexer.load_obj(main_dir, name='main terms dictionary', directory='')
    cities_posting.get()

    return total_doc_count, len(term_dict)

def merge_tokens_dictionary(main_dir):
    """
    Merges tokens dictionaries
    :return: merged dictionary
    """
    terms_dict = {}
    for file in os.listdir(main_dir + 'dictionary\\'):
        temp_dict = Indexer.load_obj(main_dir, file[:-4], directory='dictionary')
        if not temp_dict is None:
            terms_dict = {**terms_dict, **temp_dict}
    return terms_dict

def dump_proceesed_docs_to_disk(main_dir, jobs, batch_size, next_batch_num, stem):
    """
    Writing the processed data to the disk before reading more files
    :param jobs: jobs of documents
    :param batch_size: how many files to write to disk per batch
    :param next_batch_num: next batch index
    :return: count of how many documents we processed and the number of writing to disk batches we did
    """
    doc_count = 0
    temp_doc_count = 0
    batch_jobs = []
    batch_count = next_batch_num

    for job in jobs:
        new_docs_num = job.get().doc_count
        doc_count += new_docs_num
        temp_doc_count += new_docs_num
        if temp_doc_count > batch_size:
            # print('started batch num: ' + str(batch_count))
            job = pool.apply_async(batch_to_disk, (main_dir, batch_size, batch_count, q, stem))
            batch_count += 1
            batch_jobs.append(job)
            temp_doc_count -= batch_size

    # print('started batch num: ' + str(batch_count))
    job = pool.apply_async(batch_to_disk, (main_dir, temp_doc_count, batch_count, q, stem))
    batch_jobs.append(job)

    language_set = set()
    for job in batch_jobs:
        partial_language_set = job.get()
        language_set = language_set.union(partial_language_set)

    return doc_count, batch_count, language_set

def batch_to_disk(main_dir, batch_size, batch_num, q, stem):
    """
    Writing the next given amount of documents to the disk
    :param batch_size: how many documents should we write to the disk
    :param batch_num: batch serial number
    :param q: queue from which we retrieve the Document objects from
    """
    docs = []
    count = 0
    languages_partial_set = set()
    while batch_size > count:
        doc = q.get()
        if hasattr(doc, 'language'):
            languages_partial_set.add(doc.language)
        docs.append(doc)
        count += 1
    Indexer.write_docs_list_to_disk(main_dir, docs, batch_num, stem)
    return languages_partial_set

def create_tokens_posting(main_dir, stem):
    """
    Creates the token's posting file which are in a certain location in the disk
    """
    partial_terms_dictionary = {}
    prefix_tokens_dictionaries = get_list_of_files_by_prefix(main_dir)
    posting_jobs = []
    counter = 0
    batch_counter = 0
    for prefix in prefix_tokens_dictionaries:
        if counter < Preferences.posting_files_per_batch:
            counter += 1
            job = pool.apply_async(Indexer.create_prefix_posting, (main_dir, prefix, prefix_tokens_dictionaries[prefix], 'pickles', stem))
            posting_jobs.append(job)

            if counter == Preferences.posting_files_per_batch:
                counter = 0
                for job in posting_jobs:
                    prefix_dict, prefix = job.get()
                    partial_terms_dictionary[prefix] = prefix_dict
                Indexer.save_obj(partial_terms_dictionary, 'terms_dictionary', batch_counter, directory='dictionary')
                partial_terms_dictionary = {}
                batch_counter += 1



def merge_pickles_to_terms_dictionary(main_dir, stem):
    """
    Merging a given list of pickles by the prefix of the files and tokens
    """
    prefix_tokens_dictionaries = get_list_of_files_by_prefix(main_dir)
    posting_jobs = []
    for key in prefix_tokens_dictionaries.keys():
        job = pool.apply_async(Indexer.create_prefix_posting, (main_dir, key, prefix_tokens_dictionaries[key], 'pickles', stem))
        posting_jobs.append(job)

    for job in posting_jobs:
        job.get()

def get_list_of_files_by_prefix(main_dir):
    """
    Aggregate file names into groups by their prefix
    :return:
    """
    list_of_files_by_prefix = {}

    for file in os.listdir(main_dir + 'pickles\\'):
        prefix = file[:2]
        if not prefix in list_of_files_by_prefix:
            list_of_files_by_prefix[prefix] = []
        list_of_files_by_prefix[prefix].append(file[:-4])# Need to trim the last 4 chars to remove the suffix

    return list_of_files_by_prefix

def read_stop_words_lines(directory):
    """
    Reads stop words file
    :param directory: file location
    :return: returns list of stop words
    """
    try:
        stop_words_list = {}
        stop_words_file = open(directory + '\\' + 'stop_words.txt', 'r')
        for line in stop_words_file:
            if line[-1:] == '\n':
                line = line[:-1]
            if line.__contains__('\\'):
                line = line.replace('\\')
            stop_words_list[line] = 1
        return stop_words_list
    except Exception as e:
        print(e)
        print('File not found: ' + directory + 'stop_words.txt')

def remove_files(main_dir):
    directory_list = ['pickles', 'cities', 'dictionary', 'document posting', 'terms posting']

    for dir in directory_list:
        if os.path.isdir(main_dir + dir):
            shutil.rmtree(main_dir + dir)
    if os.path.isfile(main_dir + 'languages list.csv'):
        os.remove(main_dir + 'languages list.csv')
    if os.path.isfile(main_dir + 'languages.pkl'):
        os.remove(main_dir + 'languages.pkl')
    if os.path.isfile(main_dir + 'main terms dictionary.pkl'):
        os.remove(main_dir + 'main terms dictionary.pkl')
    if os.path.isfile(main_dir + 'stem main terms dictionary.pkl'):
        os.remove(main_dir + 'stem main terms dictionary.pkl')


def restart_files(main_dir):
    directory_list = ['pickles', 'cities', 'dictionary', 'document posting', 'terms posting']

    if os.path.isdir(main_dir + 'pickles'):
        shutil.rmtree(main_dir + 'pickles')

    for dir in directory_list:
        # if os.path.isdir(main_dir + dir):
        #     shutil.rmtree(main_dir + dir)
        if not os.path.isdir(main_dir + dir):
            os.mkdir(main_dir + dir)
    # if os.path.isfile(main_dir + 'languages list.csv'):
        # os.remove(main_dir + 'languages list.csv')


run_time_dir = ''

if __name__ == '__main__':
    # Debug configs:
    single_file = True
    write_to_disk = False
    parallel = True

    # main_dir = 'C:\\Chen\\BGU\\2019\\2018 - Semester A\\3. Information Retrival\\Engine\\test directory\\created files\\'
    # restart_files(main_dir)

    manager = mp.Manager()
    q = manager.Queue()
    pool = mp.Pool(processes=mp.cpu_count())


    # start_time = datetime.datetime.now()

    gui = GUI()

    # parser = Parser([read_stop_words_lines(r"C:\Users\Nitzan\Desktop\IR 2018 files desktop\FB396001")])
    # with open(r"C:\Users\Nitzan\Desktop\IR 2018 files desktop\Parser testing\Number test", 'r') as f:
    #     lines = f.readlines()
    #     result = parser.parser_pipeline(lines, False)
    #     print(result)

    # read_directory('', directory=r"C:\Users\Nitzan\Desktop\IR 2018 files desktop\FB396001",
    #                multiprocess=parallel, batch_size=20000)

    # # Single file debug config
    # if single_file:
    #     # file = ReadFile(r'C:\Users\Nitzan\Desktop\FB396001', parallel, stem, write_to_disk, q, pool)
    #     read_directory(main_dir, directory=r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\test directory\10 files', multiprocess=parallel, batch_size=20000)
    # else:
    #     # All files debug config
    #     # file = ReadFile(r'C:\Users\Nitzan\Desktop\100 file corpus', parallel)
    #     read_directory(main_dir, directory=r'C:\Chen\BGU\2019\2018 - Semester A\3. Information Retrival\Engine\corpus', multiprocess=parallel)

    # finish_time = datetime.datetime.now()
    # print(finish_time - start_time)