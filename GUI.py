from tkinter import *


root = Tk()

corpus_stopwords_label = Label(root, text='Corpus and stop-words path:')
dictionary_posting_label = Label(root, text='Dictionary and Posting path:')
language_label = Label(root, text="Language:")
stem_checkbox = Checkbutton(root, text="Use stem")

corpus_stopwords_label.grid(row=0, column=0)
dictionary_posting_label.grid(row=1, column=0)
language_label.grid(row=2, column=0)
stem_checkbox.grid(columnspan=2)


root.mainloop()