#!/usr/bin/env python
# coding=utf-8
import urllib2
import os

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
