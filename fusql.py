#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details. 


from errno import *
from stat import * 
import fuse
import os
import time

import fusqldb
import fusqlogger
import common

fuse.fuse_python_api = (0, 2)

class Metadata(fuse.Stat):
    @fusqlogger.log()
    def __init__(self, mode, isDir):
        fuse.Stat.__init__(self)
        
        if isDir:
            self.st_mode = S_IFDIR | mode
            self.st_nlink = 2
        else:
            self.st_mode = S_IFREG | mode
            self.st_nlink = 1
            
        now = int(time.time())
        self.st_atime = now
        self.st_mtime = now
        self.st_ctime = now
        self.st_uid   = os.getuid()
        self.st_gid   = os.getgid()
        self.st_size  = 0

class FuSQL(fuse.Fuse):
    @fusqlogger.log()
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.db = fusqldb.FusqlDb("test.db")
       
        root_mode = S_IRUSR|S_IXUSR|S_IWUSR|S_IRGRP|S_IXGRP|S_IXOTH|S_IROTH 
        file_mode = S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH 

        # Create shared metadata for files and directories
        self.dir_metadata = Metadata(root_mode, True)
        self.file_metadata = Metadata(file_mode, False)

        # Dictionary mapping inode_path -> (size, is_directory)
        self.paths = []
        self.paths.append('/')

        # Fill with all tables as folders
        for table_name in self.db.get_tables():
            table_path = "/" + table_name
            self.paths.append(table_path)

            table_structure = self.db.get_table_structure(table_name)

            # Fill with all rows as folders
            for row_id in self.db.get_elements_by_field("id", table_name):
                row_path = table_path + "/" + str(row_id)
                self.paths.append(row_path)

                for column in table_structure:
                    column_name = column[0]
                    column_type = column[1]

                    column_path = row_path + "/" + column_name + "." + column_type

                    self.paths.append(column_path)

    @fusqlogger.log()
    def getattr(self, path):
        spath = path.split("/")

        is_dir = len(spath) != 4

        if path in self.paths:
            if is_dir:
                result = self.dir_metadata
            else:
                table_name = spath[1]
                row_id = int(spath[2])
                column_name = spath[3].rsplit(".", 1)[0]
                data = self.db.get_element_data(table_name, column_name, row_id)

                result = self.file_metadata
                result.st_size = len(data)
        else:
            result = -ENOENT

        return result


    @fusqlogger.log()
    def open(self, path, flags):
        return 0

    @fusqlogger.log()
    def read(self, path, size, offset):
        spath = path.split("/")
        table_name = spath[1]
        element_id = int(spath[2])

        element_column = spath[3].rsplit(".", 1)[0]

        data = self.db.get_element_data(table_name, element_column, element_id)

        result = data[offset:offset+size]

        return result

    @fusqlogger.log(showReturn=True)
    def mknod(self, path, mode, rdev):
        spath = path.split("/")

        # Files MUST be inside a table and a row
        if len(spath) != 4:
            return -EPERM
        
        # Files must end in a known type
        file_type = spath[3].split(".")[-1]
        if file_type not in common.FILE_TYPE_TRANSLATOR.keys():
            return -EPERM

        table_name = spath[1]
        element_id = int(spath[2])
        column_name = spath[3].rsplit(".", 1)[0]
        column_type = common.FILE_TYPE_TRANSLATOR[file_type]

        self.db.create_column(table_name, column_name, column_type)

        # TODO: fill all elements of the table
        for dir_name in self.paths:
            if dir_name.startswith("/" + table_name + "/"):
                new_column_path = dir_name + "/" + column_name + "." + file_type
                self.paths.append(new_column_path)

        return 0

    @fusqlogger.log(showReturn=True)
    def write(self, path, buf, offset, fh=None):
        spath = path.split("/")

        table_name = spath[1]
        row_id = int(spath[2])
        column_name = spath[3].rsplit(".", 1)[0]

        prev_data = self.db.get_element_data(table_name, column_name, row_id)
        prev_size = len(prev_data)

        write_size = len(buf)

        if offset + write_size > prev_size:
            self.truncate(path, offset + write_size)
        
        new_data = prev_data[:offset] + buf + prev_data[offset+len(buf):]

        self.db.set_element_data(table_name, column_name, row_id, new_data)

        return write_size
        
    @fusqlogger.log()
    def truncate(self, path, size, fh=None):
        spath = path.split("/")

        table_name = spath[1]
        element_id = int(spath[2])
        column_name = spath[3].rsplit(".", 1)[0]

        prev_data = self.db.get_element_data(table_name, column_name, element_id)
        prev_size = len(prev_data)

        if size > prev_size:
            new_data = prev_data + (size - prev_size)*"0"
        else:
            new_data = prev_data[0:size]

        self.db.set_element_data(table_name, column_name, element_id, new_data)

        return 0

    @fusqlogger.log()
    def unlink(self, path):
        return 0

    @fusqlogger.log(showReturn=True)
    def rename(self, path_from, path_to):
        spath_from = path_from.split("/")
        spath_to = path_to.split("/")

        table_from = spath_from[1]
        table_to = spath_to[1]
        
        # Must be at the same deep
        if len(spath_from) != len(spath_to):
            return -EINVAL

        if len(spath_from) == 3:
            # If its a row
            id_from = int(spath_from[2])
            id_to = int(spath_to[2])

            if table_from != table_to:
                return -EINVAL

            self.db.set_element_data(table_to, "id", id_from, id_to)
            
        else:
            # If its a table

            self.db.rename_table(table_from, table_to)
            
        for dir_name in self.paths:
            if dir_name.startswith(path_from):
                dir_to = dir_name.replace(path_from, path_to)
                self.paths.append(dir_to)
                self.paths.remove(dir_name)
        
        return 0
    
    @fusqlogger.log()
    def chmod(self, path, mode):
        return 0
    
    @fusqlogger.log()
    def chown(self, path, uid, gid):
        return 0

    @fusqlogger.log()
    def utime(self, path, times):
        return 0

    @fusqlogger.log(showReturn=True)
    def mkdir(self, path, mode):
        spath = path.split("/")

        # Folders can only be at the root (if it's a tables)
        # or inside another folder (if it's a row)
        if len(spath) == 2:
            is_table = True
        elif len(spath) == 3:
            is_table = False
        else:
            return -EFAULT

        table_name = spath[1]
        table_path = "/" + table_name

        if is_table:
            self.db.create_table(table_name)

            self.paths.append(table_path)
        else:
            try:
                element_id = int(spath[2])
            except ValueError:
                return -EFAULT

            self.db.create_row(table_name, element_id)

            row_path = table_path + "/" + str(element_id)
            self.paths.append(row_path)
            
            table_structure = self.db.get_table_structure(table_name)
            # Fill the row with the column files

            for column in table_structure:
                column_name = column[0]
                column_type = column[1]

                column_path = row_path + "/" + column_name + "." + column_type

                self.paths.append(column_path)

        return 0

    @fusqlogger.log(showReturn=True)
    def rmdir(self, path):
        spath = path.split("/")
        result = 0

        if len(spath) == 2:
            is_table = True
        elif len(spath) == 3:
            is_table = False

        table_name = spath[1]

        def remove_paths(path):
            for i in self.paths:
                if i.startswith(path):
                    self.paths.remove(i)

        if is_table:
            table_elements = self.db.get_all_elements(table_name)

            if len(table_elements) == 0:
                self.db.delete_table(table_name)
                remove_paths(path)
            else:
                result = -ENOTEMPTY
        else:
            row_id = int(spath[2])
            self.db.delete_table_element(table_name, row_id)
            remove_paths(path)

        return result

    @fusqlogger.log()
    def readdir(self, path, offset):
        result = ['.', '..']

        if path != "/":
            path = path + "/"
        
        for i in self.paths:
            if i.startswith(path) and i != "/":
                name = i.split(path)[1]
                name = name.split("/")[0]

                if name not in result:
                    result.append(name)
        
        for i in result:
                yield fuse.Direntry(i)

    @fusqlogger.log()
    def release(self, path, fh=None):
        return 0

if __name__ == '__main__':

    fs = FuSQL()
    fs.parse(errex=1)
    fs.main()
    
