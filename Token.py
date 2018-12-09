
class Token:
    """
    Token object represents a token at the beginning of the run and term in the end
    """
    def __init__(self, token_name = None, disk_string = None):
        if disk_string is not None:
            self._define_params_from_string(disk_string)
        else:
            self.token_name = token_name
            self.df = 0
            self.doc_dict = {}
            self.tf = 0

    def add_data(self, doc_num, doc_pointer, list):
        """
        Adding data from a document to the token
        :param doc_num: document ID
        :param doc_pointer: document pointer
        :param list: list of parameter regarding the token from the document
        """
        self.df += 1
        self.tf += list[0]
        self.doc_dict[doc_num] = (list[0], list[1], list[2], doc_pointer)

    def string_to_disk(self):
        """
        Converting a token object to string for writing to the disk without the pointers to the posting files
        :return:
        """
        params = []
        params.append(str(self.token_name))
        params.append(str(self.df))
        params.append(str(self.tf))

        for k, v in self.doc_dict:
            params.append(k + ' ' + v + ',')

        return ' '.join(params)

    def _define_params_from_string(self, params_string):
        """
        Define token's parameter from a string
        :param params_string: string with parameters
        """
        params_list = params_string.split()
        self.token_name = params_list[0]
        self.df = params_list[1]
        self.tf = params_list[2]
        self.doc_dict = self._create_doc_dict_from_string(params_string[3:])


    def _create_doc_dict_from_string(self, list_of_docs_string):
        """
        Creates token's documents dictionary fro a string
        :param list_of_docs_string: string with parameters of the documents
        """
        self.doc_dict = {}

        for string in list_of_docs_string:
            string = string.split()
            self.doc_dict[string[0]] = string[1:]


    def create_string_from_doc_dictionary(self):
        """
        Creates a string with all the parameters o the documents that are in the token's dictionary
        :return: String with all the parameters
        """
        dict_str = ''
        doc_strings = []
        for doc_id in self.doc_dict:
            doc_attributes = self.doc_dict[doc_id]
            doc_strings.append(''.join(['< ', doc_id, ' ', str(doc_attributes[0]), ' ', str(doc_attributes[1]), ' ',
                                        str(doc_attributes[2]), ' ', str(doc_attributes[3]), ' >', ' ']))
        doc_strings.append('\n')
        return ''.join(doc_strings)

    def merge_tokens(self, second_token):
        """
        Merging two tokens, used when we encounter two tokens with the same name from different batches
        and we want to make them into a term.
        :param second_token: Second token to merge into the first one
        """
        self.tf += second_token.tf
        self.df += second_token.df
        self.doc_dict = {**self.doc_dict, **second_token.doc_dict}
