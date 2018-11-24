from tkinter import *
from tkinter import messagebox
import os

class GUI:

    def __init__(self):
        # self.language_list = languages_list
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
        self.activate_button = Button(self.bottom_frame, text='Activate', height=2, width=7, command=self.activate_button)
        self.reset_button = Button(self.bottom_frame, text='Reset', height=2, width=7, command=self.reset_button)
        self.view_dict_button = Button(self.bottom_frame, text='View\nDictionary')
        self.load_dict_button = Button(self.bottom_frame, text='Load\nDictionary')

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

        self.language_label.grid(row=2, column=0, sticky=E)

        self.stem_checkbox.grid(row=2, column=3, sticky=E)

        self.result1_label.grid(row=4, column=0, sticky=E)
        self.result1_entry.grid(row=4, column=1, sticky=W)

        self.result2_label.grid(row=5, column=0, sticky=E)
        self.result2_entry.grid(row=5, column=1, sticky=W)

        self.result3_label.grid(row=6, column=0, sticky=E)
        self.result3_entry.grid(row=6, column=1, sticky=W)

        self.activate_button.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.reset_button.grid(row=0, column=1, padx=5)
        self.view_dict_button.grid(row=0, column=2, padx=5)
        self.load_dict_button.grid(row=0, column=3, padx=5)

        self.root.mainloop()

    # def gui_pipeline(self):

    def check_paths(self, path, dir_name):
        if path is None:
            messagebox.showerror('Error Message', 'Field ' + dir_name + ' is empty.')
            return False
        if not os.path.exists(path):
            messagebox.showerror('Error Message', 'Field ' + dir_name + ' is empty.')
            return False
        return True


    def activate_button(self):
        corpus_path = self.corpus_stopwords_entry.get()
        output_path = self.dictionary_posting_entry.get()
        if self.check_paths(corpus_path, 'Corpus and stop-words'):
            if self.check_paths(output_path, 'Dictionary and Posting'):
                # activate readfile with both paths.
                print('Activate button is activated')



    def reset_button(self):
        # TODO: Needs to delete all files in the second path given (posting and dictionary)
        messagebox.showinfo("Reset Results", 'Posting and dictionary files have been deleted successfully')

    def update_option_menu(self, alist):
        menu = self.drop_down_menu["menu"]
        menu.delete(0, "end")
        for string in alist:
            menu.add_command(label=string,
                             command=lambda value=string: self.variable.set(value))


example = GUI()
print('Sup')



