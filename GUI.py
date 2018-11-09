from tkinter import *


class GUI:

    def __init__(self):
        root = Tk()
        root.geometry('500x300')
        root_frame = Frame(root, width=500, height=300)
        root_frame.pack(side=TOP)

        # *** Labels ***
        corpus_stopwords_label = Label(root_frame, text='Corpus and stop-words path:')
        dictionary_posting_label = Label(root_frame, text='Dictionary and Posting path:')
        language_label = Label(root_frame, text="Language:")

        # *** Entries - text boxes ***
        corpus_stopwords_entry = Entry(root_frame, width=100)
        dic_posting_entry = Entry(root_frame, width=100)

        # *** Stem checkbox ***
        stem_checkbox = Checkbutton(root_frame, text="Use stem")

        # *** Status bar ***

        # *** Language drop-down menu ***
        variable = StringVar(root)
        variable.set("Select language")  # default value
        drop_down_menu = OptionMenu(root_frame, variable, "English", "Hebrew", "Yo Mama")
        drop_down_menu.grid(row=2, column=1, sticky=W)

        # *** using grid ***

        corpus_stopwords_label.grid(row=0, column=0, sticky=E)
        dictionary_posting_label.grid(row=1, column=0, sticky=E)
        language_label.grid(row=2, column=0, sticky=E)

        corpus_stopwords_entry.grid(row=0, column=1, sticky=E + W)
        dic_posting_entry.grid(row=1, column=1, sticky=E + W)

        stem_checkbox.grid(row=3, column=0, sticky=W)

        root.mainloop()

example = GUI()


