#!/usr/bin/env python
# -*- coding: utf-8 -*-
from errno import *
from stat import * 
import fuse
import os
import time
import sqlite3

fuse.fuse_python_api = (0, 2)

class Inode:
    def __init__(self, path, mode, isDir=False):
        self.path = path
        self.metadata = fuse.Stat()
        
        if isDir:
            self.metadata.st_mode = S_IFDIR | mode
            self.metadata.st_nlink = 2
        else:
            self.metadata.st_mode = S_IFREG | mode
            self.metadata.st_nlink = 1
            self.metadata.st_size = 0
            
        now = int(time.time())
        self.metadata.st_atime = now
        self.metadata.st_mtime = now
        self.metadata.st_ctime = now
        self.metadata.st_uid   = os.getuid()
        self.metadata.st_gid   = os.getgid()

class FuSQL(fuse.Fuse):
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
       
        root_mode = S_IRUSR|S_IXUSR|S_IWUSR|S_IRGRP|S_IXGRP|S_IXOTH|S_IROTH
 
        self.inodes = {'/': Inode("/", root_mode, True)}

    def getattr(self, path):
        if path in self.hashtable:
            return self.hashtable[path].metadata
        else:
            return -ENOENT


    def open(self, path, flags):
        return 0

    def read(self, path, size, offset):
        result = ''
        
        return result


    def mknod(self, path, mode, rdev):
        return 0

    def write(self, path, buf, offset, fh=None):
        return len(buf)
        
    
    def truncate(self, path, size, fh=None):
        return 0

    def unlink(self, path):
        return 0

    def rename(self, path_from, path_to):
        return 0
    
    def chmod(self, path, mode):
        return 0
    
    def chown(self, path, uid, gid):
        return 0

    def utime(self, path, times):
        return 0

    def mkdir(self, path, mode):
        return 0

    def rmdir(self, path):
        return 0

    def readdir(self, path, offset):
        result = ['.', '..']

        for i in result:
            if i:
                yield fuse.Direntry(i)

    def release(self, path, fh=None):
        return 0

if __name__ == '__main__':

    fs = SimpleFS()
    fs.parse(errex=1)
    fs.main()
    
