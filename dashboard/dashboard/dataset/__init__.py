

class Dataset():

    def __init__(self, counter=0):
        self.counter = counter

    def get_counter(self):
        return self.counter

    def reset_counter(self):
        self.counter = 0

    def inc_counter(self, step=1):
        self.counter += step
