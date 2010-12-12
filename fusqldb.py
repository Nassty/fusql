import sqlite3

class FusqlDb(object):

    def __init__(self, database):
        self.database = database
        self.conn = sqlite3.connect(database)
        self.cursor = self.conn.cursor()

    def get_element(self, table, id):
        '''Returns all elements of table's
           row with a certain id'''

        sql = "SELECT * FROM %s WHERE id = %d" % (table, id)
        self.cursor.execute(sql)
        return self.cursor[0]

    def get_tables(self):
        '''Returns a list with the names of 
           the database tables'''

        sql = "SELECT name FROM sqlite_master"

        self.cursor.execute(sql)

        result = []
        for element in self.cursor:
            result.append(element[0])
        return result

    def get_table_structure(self, table):
        '''Returns a list of tuples (name, type) with the
           table columns name and type'''

        sql = "PRAGMA TABLE_INFO(%s)" % table

        self.cursor.execute(sql)

        result = []
        for element in self.cursor:
            result.append((element[1], element[2]))

        return result
