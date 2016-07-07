#!/usr/bin/env python
#coding=utf-8

import os
import sys
import time
import shutil
import zipfile
import urllib2

def checksync(remotedir,localdir,projectname,playpath):
    pymdir = os.path.join(localdir,'pym')
    sys.path.append(pymdir)
    import pyutil

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
        print time.strftime('%Y-%m-%d %H:%M:%S')+'：%s暂无更新，当前版本号为：%s' % (projectname,rv)
    else:
        pyutil.projectcontroller(playpath,'stop',localproject)
        try:
            pyutil.downloadFile('%s/%s/%s.zip' % (remoteproject,rv.strip(),projectname),zfile)
        except:
            print 'not found %s/%s/%s.zip' % (zfile,rv.strip(),projectname)
        if os.path.exists(configdir):
            shutil.rmtree(configdir)
        shutil.rmtree(localproject)

        f = zipfile.ZipFile(zfile)
        f.extractall(localdir)

        if os.path.exists(newver):
            shutil.copy(newver,localproject)

        pyutil.projectcontroller(playpath,'start',localproject)
        print time.strftime('%Y-%m-%d %H:%M:%S')+'：%s由%s版本更新至%s版本成功！' % (projectname,lv[:-1],rv)

def checksyncmod():
    remotedir = 'http://192.168.3.66:8080/takepackage/22010000005'
    localdir = '/home/lee'
    projectname = 'BusSync'
    playpath = '/home/lee/play-1.2.3/play'
    checksync(remotedir,localdir,projectname,playpath)