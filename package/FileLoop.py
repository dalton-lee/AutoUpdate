#!/usr/bin/env python
#coding=utf-8

import os
import json
import hashlib

def search(dir, allfile):
    items = os.listdir(dir)
    for file in items:
        filename = getAbsPath(dir, file)
        if isFile(filename):
            cur = myfile()
            cur.md5code = GetFileMd5(filename)
            cur.filename = filename
            allfile.append(cur)
        else:
            search(filename, allfile)
    return allfile

def GetFileMd5(filename):
    if not isFile(filename):
        return
    myhash = hashlib.md5()
    f = file(filename,'rb')
    while True:
        b = f.read(8096)
        if not b :
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest().upper()

class myfile:
    def __init__(self):
        self.md5code = ""
        self.filename = ""

def generate(allfile, root):
    for myfile in allfile:
        filemd5 = myfile.md5code
        filename = myfile.filename
        filelast = filename[filename.find('play-1.2.3')+11:]
        filelast = filelast.replace('\\','/').strip()
        filelast = filelast.decode('gbk').encode("utf8")
        root[filemd5] = filelast

def getAbsPath(dir, file):
    return os.path.join(dir, file)

def isFile(absPath):
    if os.path.isfile(absPath):
        return True
    return False

def createDict(path, root):
    pathList = os.listdir(path)
    for i, item in enumerate(pathList):
        if isDir(getJoinPath(path, item)):
            path = getJoinPath(path, item)
            root[item] = {}
            createDict(path, root[item])
            path = '\\'.join(path.split('\\')[:-1])
        else:
            root[item] = item

if __name__=='__main__':
    import random
    fv = open('version','w')
    fv.write(str(random.random()))
    fv.close()
    allfile = []
    root = {}
    dir = 'C:\glassfish3\glassfish\domains\domain1\docroot\play-1.2.3'
    search(dir, allfile)
    generate(allfile,root)
    filejson = json.dumps(root,ensure_ascii=False)
    f = open("filemd5.json",'w')
    f.write(filejson)
    f.close()
