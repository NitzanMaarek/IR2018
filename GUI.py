from tkinter import *

class GUI:

    def __init__(self):
        root = Tk()
        root.title('IR2018')
        root.geometry('610x300')
        top_frame = Frame(root, width=550)
        top_frame.pack(side=TOP)
        bottom_frame = Frame(root, width=550, height=300)
        bottom_frame.pack(side=BOTTOM)

        # *** Labels ***
        corpus_stopwords_label = Label(top_frame, text='Corpus and stop-words path:')
        dictionary_posting_label = Label(top_frame, text='Dictionary and Posting path:')
        language_label = Label(top_frame, text='Language:')
        result1_label = Label(top_frame, text='Number of documents indexed:')
        result2_label = Label(top_frame, text='Number of unique terms found in Corpus:')
        result3_label = Label(top_frame, text='Total runtime (in seconds):')


        # *** Entries - text boxes ***
        corpus_stopwords_entry = Entry(top_frame, width=50)
        dic_posting_entry = Entry(top_frame, width=50)
        result1_entry = Entry(top_frame)
        result2_entry = Entry(top_frame)
        result3_entry = Entry(top_frame)

        # *** Stem checkbox ***
        stem_checkbox = Checkbutton(top_frame, text="Use stem")

        # *** Buttons ***
        activate_button = Button(bottom_frame, text='Activate')
        reset_button = Button(bottom_frame, text='Reset')
        view_dict_button = Button(bottom_frame, text='View\nDictionary')
        load_dict_button = Button(bottom_frame, text='Load\nDictionary')

        # *** Status bar ***

        # *** Language drop-down menu ***
        variable = StringVar(root)
        variable.set("Select language")  # default value
        drop_down_menu = OptionMenu(top_frame, variable, "English", "Hebrew", "Yo Mama")
        drop_down_menu.grid(row=2, column=1, sticky=W)

        # *** using grid ***
        corpus_stopwords_label.grid(row=0, column=0, sticky=E)
        corpus_stopwords_entry.grid(row=0, column=1)

        dictionary_posting_label.grid(row=1, column=0, sticky=E)
        dic_posting_entry.grid(row=1, column=1)

        language_label.grid(row=2, column=0, sticky=E)

        stem_checkbox.grid(row=2, column=3, sticky=E)

        result1_label.grid(row=4, column=0, sticky=E)
        result1_entry.grid(row=4, column=1, sticky=W)

        result2_label.grid(row=5, column=0, sticky=E)
        result2_entry.grid(row=5, column=1, sticky=W)

        result3_label.grid(row=6, column=0, sticky=E)
        result3_entry.grid(row=6, column=1, sticky=W)

        activate_button.grid(row=0, column=0)
        reset_button.grid(row=0, column=1)
        view_dict_button.grid(row=0, column=2)
        load_dict_button.grid(row=0, column=3)

        root.mainloop()

example = GUI()
print('Sup')

