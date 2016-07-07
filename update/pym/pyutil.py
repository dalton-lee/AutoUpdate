#!/usr/bin/env python
# coding=utf-8

import os
import urllib2
import platform
import logging.handlers

log = logging.getLogger()

def rotatelog(filepath):
    
    global log
    log.setLevel(logging.DEBUG)
    
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(filename)s[%(lineno)d] %(levelname)-8s %(message)s')
    consoleHandler.setFormatter(fmt)
    
    handler = logging.handlers.RotatingFileHandler(filename=filepath, maxBytes=1024*1024*2, backupCount=100, encoding='utf-8')
#    filters = logging.Filter('mylogger')
#    handler.addFilter(filters)
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s %(filename)s[%(lineno)d] %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    
    log.addHandler(consoleHandler)
    log.addHandler(handler)

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
    
def projectcontrollerwin(action,servicename):
    os.system('%s %s %s' % ('net',action,servicename))

def printf(string):
    if(platform.system() != 'Windows'):
        print (string)
    else:
        print (string.decode('utf-8').encode('gbk'))