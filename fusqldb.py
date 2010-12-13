import sqlite3

class FusqlDb(object):

    def __init__(self, database):
        self.database = database
        self.conn = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
    def get_elements(self, table_name, element_id):
        '''Returns all elements of table's
           row with a certain id'''

        sql = "SELECT * FROM '%s' WHERE id = %d" % (table_name, element_id)
        response = self.cursor.execute(sql)
        return response.fetchone() 

    def get_all_elements(self, table_name):
        '''Returs all elements of a table'''
        
        sql = "SELECT * FROM '%s'" % table_name
        response = self.cursor.execute(sql)
        return response.fetchall()

    def get_element(self, table):

        sql = "SELECT id from %s" %(table)
        response = self.cursor.execute(sql)
        return [x[0] for x in response]

    def get_tables(self):
        '''Returns a list with the names of 
           the database tables'''

        sql = "SELECT name FROM sqlite_master WHERE name != 'sqlite_sequence'"

        self.cursor.execute(sql)

        result = []
        for element in self.cursor:
            result.append(element[0].encode("ascii"))
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

    def get_element_data(self, table_name, element_id):
        '''Returns ini formated string with all the
           table fields and data'''
        result = ""

        data = self.get_elements(table_name, element_id)
        structure = self.get_table_structure(table_name)

        index = 0
        for d in data:
            result += structure[index][0] + " = "
            result += str(d) + "\n"
            index += 1

        result = result.encode("ascii")

        return result

    def create_table(self, table_name):
        '''Creates a table with an id column'''

        sql = "CREATE TABLE '%s' " % table_name
        sql += "('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL)"

        self.cursor.execute(sql)

    def delete_table(self, table_name):
        '''Removes a table from the database'''

        sql = "DROP TABLE '%s'" % table_name

        self.cursor.execute(sql)
