#!/usr/bin/env python
# -*- coding: utf-8 -*-
from errno import *
from stat import * 
import fuse
import os
import time

fuse.fuse_python_api = (0, 2)

class Inode:
    def __init__(self, mode, isDir=False):
        self.data = ""
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

class SimpleFS(fuse.Fuse):
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
       
        root_mode = S_IRUSR|S_IXUSR|S_IWUSR|S_IRGRP|S_IXGRP|S_IXOTH|S_IROTH
 
        self.hashtable = {'/': Inode(root_mode, True)}

    def getattr(self, path):
        if path in self.hashtable:
            return self.hashtable[path].metadata
        else:
            return -ENOENT


    def open(self, path, flags):
        return 0

    def read(self, path, size, offset):
        result = ''
        
        data = self.hashtable[path].data
        metadata = self.hashtable[path].metadata

        file_size = len(data)
        if offset < file_size:
            if offset + size > file_size:
                size = file_size - offset
            result = data[offset:offset+size]
        
        metadata.st_atime = time.time()

        return result


    def mknod(self, path, mode, rdev):
        self.hashtable[path] = Inode(mode)
        
        return 0

    def write(self, path, buf, offset, fh=None):
        node = self.hashtable[path]
        content = node.data
        write_size = len(buf)
        
        if offset + write_size > node.metadata.st_size:
            self.truncate(path, offset + write_size)

        new_content = content[:offset] + buf + content[offset+len(buf):]
        
        node.data = new_content
        node.metadata.st_size = len(new_content)
        
        now = int(time.time())
        node.metadata.st_mtime = now
        node.metadata.st_ctime = now
        
        return len(buf)
        
    
    def truncate(self, path, size, fh=None):
        node = self.hashtable[path]
        data = node.data
        metadata = node.metadata
        node_size = metadata.st_size
        
        if size > node_size:
            new_data =  data + (node_size - size)*'\0'
        else:
            new_data = data[0:size]
    
        node.data = new_data
        metadata.st_size = len(new_data)
        
        now = time.time()
        metadata.st_ctime = now
        metadata.st_mtime = now
    
        return 0

    def unlink(self, path):
        self.hashtable.pop(path)
        
        return 0

    def rename(self, path_from, path_to):
        self.hashtable[path_to] = self.hashtable[path_from]
        self.hashtable.pop(path_from)

        return 0
    
    def chmod(self, path, mode):
        metadata = self.hashtable[path].metadata
        metadata.st_mode = mode
        metadata.st_ctime = time.time()
        return 0
    
    def chown(self, path, uid, gid):
        metadata = self.hashtable[path].metadata
        metadata.st_gid = uid
        metadata.st_gid = gid
        metadata.st_ctime = time.time()
        return 0

    def utime(self, path, times):
        metadata = self.hashtable[path].metadata

        now = time.time()
        metadata.st_atime = now
        metadata.st_mtime = now
        metadata.st_ctime = now

        return 0

    def mkdir(self, path, mode):
        self.hashtable[path] = Inode(mode, True)
        return 0

    def rmdir(self, path):
        is_empty = True
        result = 0
        
        if path != "/":
            path = path + "/"

        for i in self.hashtable.keys():
            if not is_empty:
                break

            if i.startswith(path) and i != path:
                is_empty = False

        if is_empty:
            if path != "/":
                path = path[:-1]
            self.hashtable.pop(path)
        else:
            result = -ENOTEMPTY

        return result

    def readdir(self, path, offset):
    
        result = ['.', '..']

        if path != "/":
            path = path + "/"
        
        for i in self.hashtable.keys():
            if i.startswith(path):

                name = i.split(path)[1]
                name = name.split("/")[0]

                if name not in result:
                    result.append(name)
        
        for i in result:
            if i:
                yield fuse.Direntry(i)

    def release(self, path, fh=None):
        return 0

if __name__ == '__main__':

    fs = SimpleFS()
    fs.parse(errex=1)
    fs.main()
    
