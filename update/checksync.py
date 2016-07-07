#!/usr/bin/env python
#coding=utf-8

import os
import time
import shutil
import zipfile
import urllib2

def checksync(remotedir,localdir,projectname,playpath):
    if not remotedir.endswith('/'):
        remoteproject = remotedir + '/' + projectname
    else:
        remoteproject = remotedir + projectname

    localproject = os.path.join(localdir,projectname)
    if not os.path.isdir(localproject):
        os.makedirs(localproject)
    
    rverfile = remoteproject + '/version'
    lverfile = os.path.join(localproject,'version')
    
    zfile = os.path.join(localdir,'%s.zip' % projectname)
    configdir = os.path.join(localdir,'updateconfig')
    
    newver = os.path.join(configdir,'version')
    
    while(True):
        rv = '1'
        try:
            rv = urllib2.urlopen(rverfile).read()
        except:
            print 'Connection refused: %s' % rverfile

        lv = '0'
        try:
            lv = open(lverfile).read()
        except:
            print 'Can\'t find local version file:%s' % lverfile

        if rv.strip() == lv.strip() :
            print time.strftime('%Y-%m-%d %H:%M:%S')+' 暂无更新，当前版本号为：%s' % rv
        else:
            action(playpath,'stop',localproject)
            try:
                downloadFile('%s/%s/%s.zip' % (remoteproject,rv.strip(),projectname),zfile)
            except:
                print 'not found %s/%s/%s.zip' % (zfile,rv.strip(),projectname)
                time.sleep(60)
                continue
            if os.path.exists(configdir):
                shutil.rmtree(configdir)
            shutil.rmtree(localproject)

            f = zipfile.ZipFile(zfile)
            f.extractall(localdir)

            if os.path.exists(newver):
                shutil.copy(newver,localproject)

            action(playpath,'start',localproject)
            print time.strftime('%Y-%m-%d %H:%M:%S')+' 由%s版本更新至%s版本成功！' % (lv[:-1],rv)
        time.sleep(60)

def action(playpath,action,project):
    os.system('%s %s %s' % (playpath,action,project))

def downloadFile(url,tofile):
    f = urllib2.urlopen(url)
    outf = open(tofile,'wb')        
    while True:
        s = f.read(1024*32)
        if len(s) == 0:
            break
        outf.write(s)
    outf.close()

if __name__=='__main__':
    remotedir = 'http://192.168.3.66:8080/takepackage/22010000005'
    localdir = '/home/lee'
    projectname = 'BusSync'
    playpath = '/home/lee/play-1.2.3/play'
    checksync(remotedir,localdir,projectname,playpath)