import sqlite3

class History:
    history_info = []

    def __init__(self, info):
        self.info = info
        self.preservation()


    def preservation(self):
        self.history_info += self.info
