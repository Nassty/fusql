#!/usr/bin/env python
# -*- coding: utf-8 -*-
from errno import *
from stat import * 
import fuse
import os
import time
import fusqldb

fuse.fuse_python_api = (0, 2)

class Metadata(fuse.Stat):
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
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.db = fusqldb.FusqlDb("test.db")
       
        root_mode = S_IRUSR|S_IXUSR|S_IWUSR|S_IRGRP|S_IXGRP|S_IXOTH|S_IROTH 
        file_mode = S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH 

        # Create shared metadata for files and directories
        self.dir_metadata = Metadata(root_mode, True)
        self.file_metadata = Metadata(file_mode, False)

        # Dictionary mapping inode_path -> (size, is_directory)
        self.inodes = {}
        self.inodes['/'] = {"size":0, "is_dir":True}

        # Fill with all tables as folders
        for table_name in self.db.get_tables():
            table_path = "/" + table_name
            self.inodes[table_path] = {"size": 0, "is_dir": True}

            table_structure = self.db.get_table_structure(table_name)

            # Fill with all rows as folders
            for row_id in self.db.get_elements_by_field("id", table_name):
                row_path = table_path + "/" + str(row_id)
                self.inodes[row_path] = {"size": 0, "is_dir": True}

                for column in table_structure:
                    column_name = column[0]
                    column_type = column[1]

                    column_path = row_path + "/" + column_name + "." + column_type

                    size = self.db.get_element_size(table_name, column_name, row_id)
                    self.inodes[column_path] = {"size": size, "is_dir": False}

    def getattr(self, path):
        if path in self.inodes:
            if self.inodes[path]["is_dir"]:
                result = self.dir_metadata
            else:
                result = self.file_metadata
                result.st_size = self.inodes[path]["size"]
        else:
            result = -ENOENT

        return result


    def open(self, path, flags):
        return 0

    def read(self, path, size, offset):
        spath = path.split("/")
        table_name = spath[1]
        element_id = int(spath[2].replace(".ini", ""))

        result = self.db.get_element_data(table_name, element_id)
        result = result[offset:offset+size]

        return result

    def mknod(self, path, mode, rdev):
        spath = path.split("/")

        # Not allowed more deep than 1 folder
        # Or files on root
        if len(spath) != 3:
            return -EPERM
        
        # Files must end in .ini
        if not spath[2].endswith(".ini"):
            return -EPERM

        table_name = spath[1]

        try:
            element_id = int(spath[2].replace(".ini", ""))
        except ValueError:
            # Invalid file name, must be a number
            return -EPERM

        self.db.create_table_element(table_name, element_id)
        self.inodes[path] = Inode(path, mode)
        
        element_data = self.db.get_element_data(table_name, element_id)
        self.inodes[path].metadata.st_size = len(element_data)

        return 0

    def write(self, path, buf, offset, fh=None):
        return len(buf)
        
    
    def truncate(self, path, size, fh=None):
        return 0

    def unlink(self, path):
        spath = path.split("/")
        table_name = spath[1]
        element_id = int(spath[2].replace(".ini", ""))

        self.db.delete_table_element(table_name, element_id)
        self.inodes.pop(path)

        return 0

    def rename(self, path_from, path_to):
        spath_from = path_from.split("/")
        spath_to = path_to.split("/")

        table_from = spath_from[1]
        table_to = spath_to[1]
        
        id_from = int(spath_from[2].replace(".ini", ""))
        id_to = int(spath_to[2].replace(".ini", ""))

        if table_from != table_to:
            return -1

        
        self.db.update_table_field_by_id(table_to, id_from, "id", id_to)
        
        self.inodes[path_to] = self.inodes[path_from]

        # Update node data
        element_data = self.db.get_element_data(table_to, id_to)
        self.inodes[path_to].path = path_to
        self.inodes[path_to].metadata.st_size = len(element_data)

        self.inodes.pop(path_from)

        return 0
    
    def chmod(self, path, mode):
        metadata = self.inodes[path].metadata
        metadata.st_mode = mode
        metadata.st_ctime = time.time()
        return 0
    
    def chown(self, path, uid, gid):
        metadata = self.inodes[path].metadata
        metadata.st_gid = uid
        metadata.st_gid = gid
        metadata.st_ctime = time.time()
        return 0

    def utime(self, path, times):
        metadata = self.inodes[path].metadata

        now = time.time()
        metadata.st_atime = now
        metadata.st_mtime = now
        metadata.st_ctime = now
        return 0

    def mkdir(self, path, mode):
        spath = path.split("/")

        # Folders can be only created at the root
        if len(spath) != 2:
            return -EFAULT

        table_name = spath[1]

        self.db.create_table(table_name)

        table_path = "/" + table_name
        self.inodes[table_path] = Inode(table_path, mode, True)

        return 0

    def rmdir(self, path):
        result = 0
        table_name = path.split("/")[1]

        table_elements = self.db.get_all_elements(table_name)

        if len(table_elements) == 0:
            self.db.delete_table(table_name)
            self.inodes.pop(path)
        else:
            result = -ENOTEMPTY
    
        return result

    def readdir(self, path, offset):
        result = ['.', '..']

        if path != "/":
            path = path + "/"
        
        for i in self.inodes.keys():
            if i.startswith(path) and i != "/":
                name = i.split(path)[1]
                name = name.split("/")[0]

                if name not in result:
                    result.append(name)
        
        for i in result:
                yield fuse.Direntry(i)

    def release(self, path, fh=None):
        return 0

if __name__ == '__main__':

    fs = FuSQL()
    fs.parse(errex=1)
    fs.main()
    
