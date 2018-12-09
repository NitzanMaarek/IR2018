from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import datetime
import os
import multiprocessing as mp
import Indexer
from ReadFile import ReadFile
import Preferences
import shutil
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
        # TODO: add list to drop_down_menu
        self.root = Tk()
        self.root.title('IR2018')
        self.root.geometry('610x200')
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

        # *** Entries - text boxes ***
        self.corpus_stopwords_entry = Entry(self.top_frame, width=50)
        self.dictionary_posting_entry = Entry(self.top_frame, width=50)
        self.result1_entry = Entry(self.top_frame)
        self.result2_entry = Entry(self.top_frame)
        self.result3_entry = Entry(self.top_frame)

        # *** Stem checkbox ***
        self.stem_checkbox = Checkbutton(self.top_frame, text="Use stem")

        # *** Buttons ***
        self.activate_button = Button(self.bottom_frame, text='Activate', height=2, width=7, command=self.activate_button_clicked)
        self.reset_button = Button(self.bottom_frame, text='Reset', height=2, width=7, command=self.reset_button_clicked)
        self.view_dict_button = Button(self.bottom_frame, text='View\nDictionary', command=self.view_dictionary_button_clicked)
        self.load_dict_button = Button(self.bottom_frame, text='Load\nDictionary', command=self.load_dictionary_button_clicked)
        self.browse_corpus_button = Button(self.top_frame, text='Browse', command=self.browse_stop_words_corpus)
        self.browse_destination_file_button = Button(self.top_frame, text='Browse', command=self.browse_destination_files)

        # *** Status bar ***

        # *** Language drop-down menu ***
        self.variable = StringVar(self.root)
        self.variable.set("Select language")  # default value
        self.drop_down_menu = OptionMenu(self.top_frame, self.variable, '<None>')   #CHECK IF LIST WORKDS
        self.drop_down_menu.grid(row=2, column=1, sticky=W, pady=4)

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
        self.result1_entry.config(state=DISABLED)

        self.result2_label.grid(row=5, column=0, sticky=E)
        self.result2_entry.grid(row=5, column=1, sticky=W)
        self.result2_entry.config(state=DISABLED)

        self.result3_label.grid(row=6, column=0, sticky=E)
        self.result3_entry.grid(row=6, column=1, sticky=W)
        self.result3_entry.config(state=DISABLED)

        self.activate_button.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.reset_button.grid(row=0, column=1, padx=5)
        self.view_dict_button.grid(row=0, column=2, padx=5)
        self.load_dict_button.grid(row=0, column=3, padx=5)

        self.root.mainloop()

    # def gui_pipeline(self):

    def check_paths(self, path, dir_name):
        """
        Method checks if path exists for dir_name, if not then show an error message
        :param path: string of path
        :param dir_name: string of entry
        :return: True if path is good, False otherwise
        """
        if path is None:
            messagebox.showerror('Error Message', 'Field ' + dir_name + ' is empty.')
            return False
        if not os.path.exists(path):
            messagebox.showerror('Error Message', 'Field ' + dir_name + ' does not exist.')
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
                print('Activate button is activated')
                read_directory(corpus_path, True, 20000)


    def reset_button_clicked(self):
        """
        Method deletes all posting files and dictionary. Also cleans main memory.
        """
        # TODO: Needs to delete all files in the second path given (posting and dictionary)
        output_path = self.dictionary_posting_entry.get()
        if self.check_paths(output_path):
            # self.delete_files_in_directory()
            shutil.rmtree(r'C:\Users\Nitzan\Desktop\IR 2018 files desktop\Created Files')
            self.term_dictionary.clear()
            messagebox.showinfo("Reset Results", 'Posting and dictionary files have been deleted successfully')

    def delete_files_in_directory(self, path):
        """
        Method deletes all files in given directory.
        Directory here exists for sure.
        :param path: Directory
        :return True if operation was success, False otherwise
        """
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
                return False
        return True

    def view_dictionary_button_clicked(self):
        """
        Method opens a window with dictionary in it.
        """
        if len(self.term_dictionary) != 0:
            # self.term_dictionary = self.load_dictionary_button_clicked()
            # self.term_dictionary = {'s': 'a', 'b': 'jay'}
            self.display_dictionary()
        else:
            messagebox.showerror('Error Message', 'No dictionary to show.\nPlease load dictionary to memory first.')
        # TODO: Show self.dictionary on a new window

    def display_dictionary(self):
        """
        Method opens a new window with the dictionary in it: displaying terms and their total frequency in text.
        """
        window = Toplevel(self.root)
        window.geometry('500x500')
        # window.title = 'Dictionary'
        scrollbar = Scrollbar(window)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox = Listbox(window)
        listbox.size()
        listbox.pack(fill="both", expand=TRUE)

        for key in self.term_dictionary.keys():
            listbox.insert(END, key)

        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)


    def load_dictionary_button_clicked(self):
        """
        Method loads dictionary to memory.
        """
        self.term_dictionary = Indexer.load_obj('main terms dictionary', 'dictionary')

    def update_option_menu(self, alist):
        """
        Method updates scroll-down menu of languages with strings in a given list.
        :param alist: list of strings (=languages)
        """
        menu = self.drop_down_menu["menu"]
        menu.delete(0, "end")
        for string in alist:
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


def read_directory(directory, multiprocess, batch_size=20000):
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

    for root, dirs, files in os.walk(directory):
        # TODO: Read also stop_words.txt from this directory and forward list to parser init
        stop_words_list = read_stop_words_lines(directory) # TODO: Figure out what is this
        for file in files:
            if not file == 'stop_words.txt':
                path = os.path.join(root, file)
                if multiprocess:
                    job = pool.apply_async(ReadFile, (file, q, path, stop_words_list))
                    jobs.append(job)
                    file_count += 1
                    if file_count == 300:
                        print('dumping files')
                        processed_docs, next_batch_num, partial_language_set = dump_proceesed_docs_to_disk(jobs, batch_size, next_batch_num)
                        language_set = language_set.union(partial_language_set)
                        next_batch_num += 1
                        total_doc_count += processed_docs
                        jobs = []
                        file_count = 0
                else:
                    ReadFile(file, q, path, stop_words_list)


    if len(jobs) > 0:
        processed_docs, next_batch_num, partial_language_set = dump_proceesed_docs_to_disk(jobs, batch_size, next_batch_num)
        language_set = language_set.union(partial_language_set)
        total_doc_count += processed_docs

    with open(Preferences.main_directory + 'languages list.csv', 'w') as cities_file:
        wr = csv.writer(cities_file, quoting=csv.QUOTE_ALL)
        wr.writerow(list(language_set))
        # cities_file.writelines()

    cities_posting = pool.apply_async(Indexer.create_cities_posting, (False, ))

    print('total docs: ' + str(total_doc_count))
    print('Until merge runtime: ' + str(datetime.datetime.now() - start_time))

    merge_pickles_to_terms_dictionary()
    print('Until saving dictionary by prefixes: ' + str(datetime.datetime.now() - start_time))

    terms_dictionary = merge_tokens_dictionary()
    print('Until saving dictionary as one file: ' + str(datetime.datetime.now() - start_time))

    print('Trying to save and load dictionary')
    Indexer.save_obj(obj=terms_dictionary, name='main terms dictionary', directory='')
    test = Indexer.load_obj(name='main terms dictionary.pkl', directory='')
    # print(test)
    cities_posting.get()

def merge_tokens_dictionary():
    """
    Merges tokens dictionaries
    :return: merged dictionary
    """
    terms_dict = {}
    for file in os.listdir(Preferences.main_directory + 'dictionary\\'):
        temp_dict = Indexer.load_obj(file[:-4], directory='dictionary')
        if not temp_dict is None:
            terms_dict = {**terms_dict, **temp_dict}
    return terms_dict

def dump_proceesed_docs_to_disk(jobs, batch_size, next_batch_num):
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
            print('started batch num: ' + str(batch_count))
            job = pool.apply_async(batch_to_disk, (batch_size, batch_count, q))
            batch_count += 1
            batch_jobs.append(job)
            temp_doc_count -= batch_size

    print('started batch num: ' + str(batch_count))
    job = pool.apply_async(batch_to_disk, (temp_doc_count, batch_count, q))
    batch_jobs.append(job)

    language_set = set()
    for job in batch_jobs:
        partial_language_set = job.get()
        language_set = language_set.union(partial_language_set)

    return doc_count, batch_count, language_set

def batch_to_disk(batch_size, batch_num, q):
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
    Indexer.write_docs_list_to_disk(docs, batch_num)
    return languages_partial_set

def create_tokens_posting():
    """
    Creates the token's posting file which are in a certain location in the disk
    """
    partial_terms_dictionary = {}
    prefix_tokens_dictionaries = get_list_of_files_by_prefix()
    posting_jobs = []
    counter = 0
    batch_counter = 0
    for prefix in prefix_tokens_dictionaries:
        if counter < Preferences.posting_files_per_batch:
            counter += 1
            job = pool.apply_async(Indexer.create_prefix_posting, (prefix, prefix_tokens_dictionaries[prefix], q))
            posting_jobs.append(job)

            if counter == Preferences.posting_files_per_batch:
                counter = 0
                for job in posting_jobs:
                    prefix_dict, prefix = job.get()
                    partial_terms_dictionary[prefix] = prefix_dict
                Indexer.save_obj(partial_terms_dictionary, 'terms_dictionary', batch_counter, directory='dictionary')
                partial_terms_dictionary = {}
                batch_counter += 1

    # TODO: check if we need to get back the dictionary

def merge_pickles_to_terms_dictionary():
    """
    Merging a given list of pickles by the prefix of the files and tokens
    """
    prefix_tokens_dictionaries = get_list_of_files_by_prefix()
    posting_jobs = []
    for key in prefix_tokens_dictionaries.keys():
        job = pool.apply_async(Indexer.create_prefix_posting, (key, prefix_tokens_dictionaries[key]))
        posting_jobs.append(job)

    for job in posting_jobs:
        job.get()

def get_list_of_files_by_prefix():
    """
    Aggregate file names into groups by their prefix
    :return:
    """
    list_of_files_by_prefix = {}

    for file in os.listdir(Preferences.main_directory + 'pickles\\'):
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
            if line.__contains__('\\'):     # TODO: Need to fix when there is \ in stopword
                line = line.replace('\\')
            stop_words_list[line] = 1
        return stop_words_list
    except Exception as e:
        print(e)
        print('File not found: ' + directory + 'stop_words.txt')


def restart_files():
    directory_list = ['pickles', 'cities', 'dictionary', 'document posting', 'terms posting']

    for dir in directory_list:
        if os.path.isdir(Preferences.main_directory + dir):
            shutil.rmtree(Preferences.main_directory + dir)
        os.mkdir(Preferences.main_directory + dir)
    if os.path.isfile(Preferences.main_directory + 'languages list.csv'):
        os.remove(Preferences.main_directory + 'languages list.csv')

if __name__ == '__main__':
    # Debug configs:
    single_file = True
    write_to_disk = False
    parallel = True
    # stem = Preferences.stem

    main_directory = Preferences.main_directory

    restart_files()

    manager = mp.Manager()
    q = manager.Queue()
    pool = mp.Pool(processes=mp.cpu_count())


    start_time = datetime.datetime.now()

    # gui = GUI()

    # Single file debug config
    if single_file:
        # file = ReadFile(r'C:\Users\Nitzan\Desktop\FB396001', parallel, stem, write_to_disk, q, pool)
        read_directory(directory=r'C:\Users\Nitzan\Desktop\IR 2018 files desktop\FB396001', multiprocess=parallel, batch_size=20000)
    else:
        # All files debug config
        # file = ReadFile(r'C:\Users\Nitzan\Desktop\100 file corpus', parallel)
        read_directory(directory=r'C:\Users\Nitzan\Desktop\IR 2018 files desktop\FB396001', multiprocess=parallel)

    finish_time = datetime.datetime.now()
    print(finish_time - start_time)