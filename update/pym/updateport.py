#!/usr/bin/env python
#coding=utf-8

import string
import codecs

def modifyconf(filepath,key,value):
    s = ""
    flag = False
    f = codecs.open(filepath)
    for line in f:
        if getkeybyline(line,key):
            flag = True
            s = s + key + " = " + value + "\r\n"
        else:
            s = s + line
    if not flag:
        s = s + "\r\n" +  key + " = " + value + "\r\n"
    f.close()
    f = codecs.open(filepath,'w')
    f.write(str)
    f.close()

def getkeybyline(line,key):
    linedef = line.strip()
    if len(linedef) == 0:
        return False
    if linedef[0] in ('!', '#'):
        return False
    if linedef.find('=') == -1:
        return False
    tkey = linedef.split('=')[0].strip()
    if (key==tkey):
        return True
    else:
        return False

def getport(filepath,key):
    if filepath.__len__() > 0:
        f = codecs.open(filepath)
        for line in f:
            if getkeybyline(line,key):
                return getvaluebykey(line,key)
        return "9000"    
        f.close()		

def getvaluebykey(line,key):
    linedef = line.strip()
    if len(linedef) == 0:
        return ""
    if linedef[0] in ('!', '#'):
        return ""
    if linedef.find('=') == -1:
        return ""
    tkey = linedef.split('=')[0].strip()
    if (key==tkey):
        return linedef.split('=')[1].strip()
    else:
        return ""

if __name__=='__main__':
    filepath = '/home/lee/BusSaletmp/conf/application.conf'
    key = 'http.port'
#    value = '7890'
    value = getport(filepath,key)
    value = str(string.atoi(value)+1)
#    for i in range(10):
#        value = str(string.atoi(value)+i)
#        if 端口通，则...
    modifyconf(filepath,key,value)