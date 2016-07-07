#!/usr/bin/env python
#coding=utf-8

import os
import json
import urllib2
import time

def checkplay(version,url,localfile,playdir,host):
    while True:
        if not os.path.isdir(playdir):
            os.mkdir(playdir)
        rs = '0'
        ls = '1'
        try:
            rs = urllib2.urlopen(version).read()
        except:
            print 'Can not find versionfile:%s' % version
        try:
            ls = open(os.path.join(playdir,'version')).read()
        except:
            print 'Can not find versionfile:%s' % playdir
        if rs.strip() == ls.strip() :
            print '暂无更新，当前版本号为：%s' % rs
        else:
            print '发现新版本，新版本号为：%s' % rs
            print '开始解析差异文件：%s' % url
            remotestr = urllib2.urlopen(url).read()
            remotedict = json.loads(remotestr)
            remotekeys = set(remotedict.keys())

            localstr = '';
            localdict = {'':''}
            try:
                localstr = open(localfile).read()
            except:
                print 'Can not find localmd5file:%s' % localfile
            try:
                localdict = json.loads(localstr)
            except:
                
                print 'Can not load md5file as json:%s' % localfile
            localkeys = set(localdict.keys())

            print '同步删除中..'
            localdiff = localkeys-remotekeys
            for local in localdiff:
                filepath = os.path.join(playdir,localdict[local])
                removefile(filepath)
                continue

            print '同步更新中..'
            remotediff = remotekeys-localkeys
            for remote in remotediff:
                path = remotedict[remote]
                remotepath = os.path.join(host,path)
                filepath = os.path.join(playdir,path)
                addfile(remotepath,filepath)
                continue
            print ('%s版本更新%s版本成功！时间：%s' % (ls,rs,time.strftime('%Y-%m-%d %H:%M:%S')))
#		checksale.check()
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
        downloadFile(remotepath,filepath)
        print 'add:%s' % filepath
    except:
        print 'failed:%s' % remotepath

def downloadFile(url,tofile):
    f = urllib2.urlopen(url)
    outf = open(tofile,'wb')        
    c = 0
    while True:
        s = f.read(1024*32)
        if len(s) == 0:
            break
        outf.write(s)
        c += len(s)
    outf.close()
    return c/1024/1024

if __name__ == '__main__':
    version = 'http://192.168.3.66:8080/takepackage/play-1.2.3/version'
    url = 'http://192.168.3.66:8080/takepackage/play-1.2.3/filemd5'
    localfile = '/home/lee/play-1.2.3/filemd5'
    playdir = '/home/lee/play-1.2.3/'
    host = 'http://192.168.3.66:8080/takepackage/play-1.2.3/'
    checkplay(version,url,localfile,playdir,host)
