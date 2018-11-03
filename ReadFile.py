import pandas as pd
import numpy as np
import os
import multiprocessing as mp
import datetime

class ReadFile:
    def __init__(self, directory):
        self.directory = directory
        self.manager = mp.Manager()
        self.q = self.manager.Queue()
        self.pool = mp.Pool(mp.cpu_count() + 2)
        self.jobs = []

    def run_file_reader(self):
        start_time = datetime.datetime.now()
        self.read_directory(self.directory)
        self.q.put(['kill'])
        self.pool.close()
        self.pool.join()
        finish_time = datetime.datetime.now()
        print(finish_time - start_time)

    def read_directory(self, directory):
        for filename in os.listdir(directory):
            if os.path.isdir(filename):
                job = self.pool.apply_async(self.read_directory, filename)
                self.jobs.append(job)
            else:
                job = self.pool.apply_async(self.read_file, filename)
                self.jobs.append(job)

    # def read_file(self, file_path):

