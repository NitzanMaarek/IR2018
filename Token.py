
class Token:
    def __init__(self, token_name = None, disk_string = None):
        if disk_string is not None:
            self._define_params_from_string(disk_string)
        else:
            self.token_name = token_name
            self.df = 0
            self.doc_dict = {}

    def add_data(self, doc_pointer, tuple, doc_num):
        self.df += 1
        self.doc_dict[doc_num] = (tuple[0], tuple[1], doc_pointer)


    def string_to_disk(self):
        """
        Converting a token object to string for writing to the disk without the pointers to the posting files
        :return:
        """
        params = []
        params.append(str(self.token_name))
        params.append(str(self.df))

        for k, v in self.doc_dict:
            params.append(k + ' ' + v + ',')

        return ' '.join(params)

    def _define_params_from_string(self, params_string):
        params_list = params_string.split()
        self.token_name = params_list[0]
        self.df = params_list[1]
        self.doc_dict = self._create_doc_dict_from_string(params_string[2:])


    def _create_doc_dict_from_string(self, list_of_docs_string):
        self.doc_dict = {}

        for string in list_of_docs_string:
            string = string.split()
            self.doc_dict[string[0]] = string[1:]


    def create_string_from_doc_dictionary(self):
        dict_str = ''
        doc_strings = []
        for doc_id in self.doc_dict:
            doc_attributes = self.doc_dict[doc_id]
            # tf = doc_attributes[0]
            # first_position = doc_attributes[1]
            # doc_pointer = doc_attributes[2]
            #TODO: need to get pointer to doc posting file
            doc_strings.append(''.join(['<', doc_id, ' ', str(doc_attributes[0]), ' ', str(doc_attributes[1]), ' ', doc_attributes[2], '>', ' ']))
        doc_strings.append('\n')
        return ''.join(doc_strings)

    def merge_tokens(self, second_token):
        self.df += second_token.df
        self.doc_dict = {**self.doc_dict, **second_token.doc_dict}

    # def add_document_pointer(self, doc_name, pointer_value):
    #     self.doc_dict[doc_name] = pointer_value