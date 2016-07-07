#!/usr/bin/env python
#coding=utf-8

import os
import sys
import json
import time
import urllib2
import platform

def checkplay(remotedir,localdir):
    if not remotedir.endswith('/'):
        rverfile = remotedir + '/' + 'version'
        rmd5file = remotedir + '/' + 'filemd5'
    else:
        rverfile = remotedir + 'version'
        rmd5file = remotedir + 'filemd5'
    lverfile = os.path.join(localdir,'version')
    lmd5file = os.path.join(localdir,'filemd5')
    while True:
        if not os.path.isdir(localdir):
            os.makedirs(localdir)
        ls = '0'
        rs = '1';
        try:
            rs = urllib2.urlopen(rverfile).read()
        except:
            print 'Can\'t find remote version file:%s' % rverfile
        try:
            ls = open(lverfile).read()
        except:
            print 'Can\'t find local version file:%s' % lverfile
        if rs.strip() == ls.strip() :
            print time.strftime('%Y-%m-%d %H:%M:%S')+'：play暂无更新，当前版本号为：%s' % (ls)
        else:
            print '发现新版本，新版本号为：%s' % rs
            print '开始解析差异文件：%s' % rmd5file
            remotestr = urllib2.urlopen(rmd5file).read()
            remotedict = json.loads(remotestr)
            remotekeys = set(remotedict.keys())

            localstr = '';
            localdict = {'':''}
            try:
                localstr = open(lmd5file).read()
            except:
                print 'Can\'t find local md5 file:%s' % lmd5file
            try:
                localdict = json.loads(localstr)
            except:
                print 'Can\'t load md5 file as json:%s' % lmd5file
            localkeys = set(localdict.keys())

            print '同步删除中..'
            localdiff = localkeys-remotekeys
            for local in localdiff:
                lpath = localdict[local].replace('/',os.path.sep)
                filepath = os.path.join(localdir,lpath)
                removefile(filepath)
                continue

            print '同步更新中..'
            remotediff = remotekeys-localkeys
            for remote in remotediff:
                rpath = remotedict[remote]
                remotepath = ''
                if not remotedir.endswith('/'):
                    remotepath = remotedir + '/' + rpath
                else:
                    remotepath = remotedir + rpath
                filepath = os.path.join(localdir,rpath.replace('/',os.path.sep))
                addfile(remotepath,filepath)
                continue
            if(platform.system() == 'Linux'):
                play = os.path.join(localdir,'play')
                os.system('chmod 744 %s' % play)
            print time.strftime('%Y-%m-%d %H:%M:%S')+'：play由%s版本更新至%s版本成功！' % (ls,rs)
        checksale3.checksalemod()
        checksync3.checksyncmod()
        time.sleep(60)

def removefile(filepath):
    parentdir = os.path.dirname(filepath)
    try:
        os.remove(filepath)
        print 'del:%s' % filepath
    except:
        print 'already del : %s' % filepath
    try:
        filelist = os.listdir(parentdir)
        if len(filelist) == 0 :
            try:
                os.rmdir(parentdir)
                print 'deldir:%s' % parentdir
            except:
                print 'already deldir : %s' % parentdir
    except:
        print '%s not exist' % parentdir

def addfile(remotepath,filepath):
    dirname = os.path.dirname(filepath)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        print 'mkdir:%s' % dirname
    try:
        pyutil.downloadFile(remotepath,filepath)
        print 'add:%s' % filepath
    except:
        print 'failed:%s' % remotepath

if __name__ == '__main__':
    remotedir = 'http://192.168.3.66:8080/takepackage/play-1.2.3/'
    localdir = '/home/lee/play-1.2.3/'
    pymdir = '/home/lee/pym'
    sys.path.append(pymdir)
    import pyutil
    import checksale3
    import checksync3
    checkplay(remotedir,localdir)