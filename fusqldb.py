# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details. 


import sqlite3

class FusqlDb(object):
    def __init__(self, database):
        '''Main api to control the database management'''

        self.database = database
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()
        
    def get_element_by_id(self, table_name, element_id):
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

    def get_elements_by_field(self, field, table):
        '''Returns an specific field of a table'''

        sql = "SELECT %s from %s" %(field, table)
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
        # I plan handle sites here. 
        special_cases =   {"start":    "html",
                           "page":     "html",
                           "style":    "css",
                           "functions":"js"}

        type_translator = {"TEXT":     "txt",
                           "INTEGER":  "int",
                           "BLOB":     "bin"}

        # TODO: Magic to guess file mimetype if it's a binary file

        self.cursor.execute(sql)

        result = []
        for element in self.cursor:
            element_name = element[1].encode("ascii")
            if element_name in special_cases.keys():
                element_type = special_cases[element_name]
            else:
                element_type = type_translator[element[2].encode("ascii")]
            if element_name == "start": # I can't name a column index,
                                        # so I handle it here
                element_name = "index"
            result.append((element_name, element_type))

        return result

    def get_element_ini_data(self, table_name, element_id):
        '''Returns ini formated string with all the
           table fields and data'''

        result = ""

        data = self.get_element_by_id(table_name, element_id)
        structure = self.get_table_structure(table_name)

        index = 0
        for d in data:
            result += structure[index][0] + " = "
            result += str(d) + "\n"
            index += 1

        result = result.encode("ascii")

        return result

    def get_element_data(self, table_name, element_column, element_id):
        '''Returns the data of a cell'''
        
        result = ""
        if element_column == "index":
            element_column = "start"

        sql = "SELECT %s FROM '%s' WHERE id = %d" % \
              (element_column, table_name, element_id)

        self.cursor.execute(sql)
        response = self.cursor.fetchone()[0]
        if response is not None:
            if type(response) == buffer:
                for b in response:
                    result += b
            else:
                result = str(response)
                result += '\n'

        return result

    def create_table(self, table_name):
        '''Creates a table with an id column'''

        sql = "CREATE TABLE '%s' " % table_name
        sql += "('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL)"
        self.cursor.execute(sql)
        self.connection.commit()

    def create_row(self, table_name, element_id):
        '''Creates a row in a table with an id'''

        sql = "INSERT INTO '%s' (id) VALUES (%d)" % (table_name, element_id)

        self.cursor.execute(sql)
        self.connection.commit()

    def delete_table(self, table_name):
        '''Removes a table from the database'''

        sql = "DROP TABLE '%s'" % table_name
        self.cursor.execute(sql)
        self.connection.commit()

    def create_table_element(self, table_name, element_id):
        '''Creates a table element'''

        sql = "INSERT INTO '%s' (id) VALUES (%d)" % (table_name, element_id)
        self.cursor.execute(sql)
        self.connection.commit()

    def delete_table_element(self, table_name, element_id):
        '''Removes an element of a table'''

        sql = "DELETE FROM '%s' WHERE id = %d" % (table_name, element_id)
        self.cursor.execute(sql)
        self.connection.commit()

    def update_table_field_by_id(self, table_name, element_id, field, value):
        '''Modifies a table field'''

        sql = "UPDATE '%s' SET '%s' = '%s' WHERE id = %d" \
              % (table_name, field, value, element_id)

        self.cursor.execute(sql)
        self.connection.commit()

