#!/usr/bin/env python
#coding=utf-8

import os
import sys
import time
import urllib2

sys.path.append('/home/lee/pym')
import updateport

def checksync(projecthost,localproject,tofile,playpath):
    versionurl = os.path.join(projecthost,'version')
    versionfile = os.path.join(localproject,'version')
    tmpproject = '%s%s' % (localproject,'tmp')
    localconf = os.path.join(localproject,'conf/application.conf')
    tmpconf = os.path.join(tmpproject,'conf/application.conf')
    while(True):
        rv = ''
        try:
            rv = urllib2.urlopen(versionurl).read()
        except:
            print 'Connection refused: %s' % versionurl

        lv = 'v'
        try:
            lv = open(versionfile).read()
        except:
            print 'Can not find versionfile:%s' % versionfile

        if rv.strip() == lv.strip() :
            print time.strftime('%Y-%m-%d %H:%M:%S')+' 暂无更新，当前版本号为：%s' % rv
        else:
            action(playpath,'stop',localproject)
            try:
                downloadFile('%s/%s/BusSync.zip' % (projecthost,rv.strip()),tofile)
            except:
                print 'not found %s/%s/BusSync.zip' % (projecthost,rv.strip())
                time.sleep(60)
                continue
            os.system('rm -rf %s' % localproject)
            os.system('unzip -oq %s -d /home/lee/' % tofile)
            action(playpath,'start',localproject)
            print time.strftime('%Y-%m-%d %H:%M:%S')+' 由%s版本更新至%s版本成功！' % (lv[:-1],rv)
        time.sleep(10)

def action(playpath,action,project):
    os.system('%s %s %s' % (playpath,action,project))

def downloadFile(url,tofile):
    f = urllib2.urlopen(url)
    outf = open(tofile,'wb')        
    c = 0
    while True:
        s = f.read(1024*32)
        if len(s) == 0:
            break
        outf.write(s)
    outf.close()

if __name__=='__main__':
    projecthost = 'http://192.168.3.66:8080/hhht/BusSync/'
    localproject = '/home/lee/BusSync'
    tofile = '/home/lee/BusSync.zip'
    playpath = '/home/lee/play-1.2.3/play'
    checksync(projecthost,localproject,tofile,playpath)
