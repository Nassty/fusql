import sqlite3

class FusqlDb(object):

    def __init__(self, database):
        self.database = database
        self.conn = sqlite3.connect(database)
        self.cursor = self.conn.cursor()
    
    def get_element(self, table, id):
        sql = "SELECT * FROM ? WHERE id = ?"
        self.cursor.execute(sql, (table, id))
        return self.cursor[0]

    def get_tree(self):
        sql = "SELECT name FROM sqlite_master"
        results = []
        for element in self.cursor:
            results.append(element)
        return results
