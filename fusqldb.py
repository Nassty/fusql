# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details. 

import sqlite3

import fusqlogger
import common

class FusqlDb(object):
    @fusqlogger.log()
    def __init__(self, database):
        '''Main api to control the database management'''

        self.database = database
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def execute_sql(self, sql, commit=True, dump=True):
        '''Executes sql, commits the database and logs the sql'''

        self.cursor.execute(sql)

        if commit:
            self.connection.commit()
        
        if dump:
            fusqlogger.dump(sql)
        
    @fusqlogger.log()
    def get_element_by_id(self, table_name, element_id):
        '''Returns all elements of table's
           row with a certain id'''

        sql = "SELECT * FROM '%s' WHERE id = %d" % (table_name, element_id)
        response = self.execute_sql(sql, False)
        return response.fetchone() 

    @fusqlogger.log()
    def get_all_elements(self, table_name):
        '''Returs all elements of a table'''
        
        sql = "SELECT * FROM '%s'" % table_name
        self.execute_sql(sql, False)
        return self.cursor.fetchall()

    @fusqlogger.log()
    def get_elements_by_field(self, field, table):
        '''Returns an specific field of a table'''

        sql = "SELECT %s from %s" %(field, table)
        self.execute_sql(sql, False)
        return [x[0] for x in self.cursor]

    @fusqlogger.log()
    def get_tables(self):
        '''Returns a list with the names of 
           the database tables'''

        sql = "SELECT name FROM sqlite_master WHERE name != 'sqlite_sequence'"
        self.execute_sql(sql, False)

        result = []
        for element in self.cursor:
            result.append(element[0].encode("ascii"))
        return result

    @fusqlogger.log()
    def get_table_structure(self, table):
        '''Returns a list of tuples (name, type) with the
           table columns name and type'''

        sql = "PRAGMA TABLE_INFO(%s)" % table
        # I plan handle sites here. 
        special_cases =   {"start":    "html",
                           "page":     "html",
                           "style":    "css",
                           "functions":"js"}

        # TODO: Magic to guess file mimetype if it's a binary file

        self.execute_sql(sql, False)

        result = []
        for element in self.cursor:
            element_name = element[1].encode("ascii")
            if element_name in special_cases.keys():
                element_type = special_cases[element_name]
            else:
                element_type = common.DB_TYPE_TRANSLATOR[element[2].encode("ascii")]
            if element_name == "start": # I can't name a column index,
                                        # so I handle it here
                element_name = "index"
            result.append((element_name, element_type))

        return result

    @fusqlogger.log()
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

    @fusqlogger.log()
    def get_element_data(self, table_name, element_column, element_id):
        '''Returns the data of a cell'''
        
        result = ""
        if element_column == "index":
            element_column = "start"

        sql = "SELECT %s FROM '%s' WHERE id = %d" % \
              (element_column, table_name, element_id)
        self.execute_sql(sql, False)

        response = self.cursor.fetchone()[0]
        if response is not None:
            if type(response) == buffer:
                for b in response:
                    result += b
            else:
                result = str(response)

        return result
    
    @fusqlogger.log(True)
    def set_element_data(self, table_name, column_name, element_id, value):
        '''Modifies a table field'''

        sql = "UPDATE '%s' SET '%s' = '%s' WHERE id = %d" \
              % (table_name, column_name, value, element_id)
        self.execute_sql(sql, dump=False)

    @fusqlogger.log()
    def create_table(self, table_name):
        '''Creates a table with an id column'''

        sql = "CREATE TABLE '%s' " % table_name
        sql += "('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL)"
        self.execute_sql(sql)

    @fusqlogger.log()
    def create_row(self, table_name, element_id):
        '''Creates a row in a table with an id'''

        sql = "INSERT INTO '%s' (id) VALUES (%d)" % (table_name, element_id)
        self.execute_sql(sql)

    @fusqlogger.log()
    def create_column(self, table_name, column_name, column_type):
        '''Creates a column in a table'''

        sql = "ALTER TABLE '%s' ADD COLUMN '%s' %s" % \
              (table_name, column_name, column_type)
        self.execute_sql(sql)

    @fusqlogger.log()
    def delete_table(self, table_name):
        '''Removes a table from the database'''

        sql = "DROP TABLE '%s'" % table_name
        self.execute_sql(sql)

    @fusqlogger.log()
    def rename_table(self, table_from, table_to):
        '''Renames a table'''

        sql = "ALTER TABLE '%s' RENAME TO '%s'" % (table_from, table_to)
        self.execute_sql(sql)

    @fusqlogger.log()
    def create_table_element(self, table_name, element_id):
        '''Creates a table element'''

        sql = "INSERT INTO '%s' (id) VALUES (%d)" % (table_name, element_id)
        self.execute_sql(sql)

    @fusqlogger.log()
    def delete_table_element(self, table_name, element_id):
        '''Removes an element of a table'''

        sql = "DELETE FROM '%s' WHERE id = %d" % (table_name, element_id)
        self.execute_sql(sql)


