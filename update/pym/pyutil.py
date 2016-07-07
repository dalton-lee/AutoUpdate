#!/usr/bin/env python
# coding=utf-8

import os
import urllib2
import platform

def downloadFile(url, tofile):
    f = urllib2.urlopen(url)
    outf = open(tofile, 'wb')        
    c = 0
    while True:
        s = f.read(1024 * 32)
        if len(s) == 0:
            break
        outf.write(s)
        c += len(s)
    outf.close()
    return c / 1024 / 1024 

def projectcontroller(playpath,action,project):
    os.system('%s %s %s' % (playpath,action,project))

def printf(string):
    if(platform.system() != 'Windows'):
        print (string)
    else:
        print (string.decode('utf-8').encode('gbk'))