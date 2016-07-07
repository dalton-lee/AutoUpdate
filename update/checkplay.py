#!/usr/bin/env python
#coding=utf-8

import os
import sys
import json
import time
import urllib2
import platform
import ConfigParser

UPDATE_CONFIG = 0

def checkplay(remotedir,workdir):
    
    global UPDATE_CONFIG
    
    if not remotedir.endswith('/'):
        remotedir = remotedir + '/'
        
    orgcode = UPDATE_CONFIG.get('global', 'orgcode')
    projectdir = remotedir + orgcode
    
    syncservice = UPDATE_CONFIG.get('BusSync', 'servicename')
    saleservice = UPDATE_CONFIG.get('BusSale', 'servicename')
    
    port = UPDATE_CONFIG.get('BusSale', 'port')
    nginx = UPDATE_CONFIG.get('BusSale', 'nginx')
    ngconf = UPDATE_CONFIG.get('BusSale', 'ngconf')
    delay = UPDATE_CONFIG.get('BusSale', 'delay')
    
    remotedir = remotedir + 'play-1.2.3/'
    localdir = os.path.join(workdir,'play-1.2.3')
    
    play = os.path.join(localdir,'play')
    
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
            printf ('Can\'t find remote version file:%s,wait for next time!' % rverfile)
            time.sleep(60)
            continue
        try:
            ls = open(lverfile).read()
        except:
            printf ('Can\'t find local version file:%s' % lverfile)
            printf ('开始生成本地MD5文件')
            try:
                os.system('python /home/lee/pym/FileLoop')
                time.sleep(10)
            except:
                printf('生成本地MD5文件失败，再说...')  
        if rs.strip() == ls.strip() :
            printf (time.strftime('%Y-%m-%d %H:%M:%S')+'：play暂无更新，当前版本号为：%s' % (ls))
        else:
            printf ('发现新版本，新版本号为：%s' % rs)
            printf ('开始解析差异文件：%s' % rmd5file)
            remotestr = ''
            try:
                remotestr = urllib2.urlopen(rmd5file).read()
            except:
                printf ('无法找到远程md5文件，请检查服务端目录或通过浏览器查看文件是否存在：%s' % rmd5file)
                printf ('等待60秒后，重新尝试更新！')
                time.sleep(60)
                continue
            remotedict = json.loads(remotestr)
            remotekeys = set(remotedict.keys())

            localstr = ''
            localdict = {'':''}
            try:
                localstr = open(lmd5file).read()
            except:
                printf ('Can\'t find local md5 file:%s' % lmd5file)
            try:
                localdict = json.loads(localstr)
            except:
                printf ('Can\'t load md5 file as json:%s' % lmd5file)
            localkeys = set(localdict.keys())

            printf ('同步删除中..')
            localdiff = localkeys-remotekeys
            for local in localdiff:
                lpath = localdict[local].replace('/',os.path.sep)
                filepath = os.path.join(localdir,lpath)
                removefile(filepath)
                continue

            printf ('同步更新中..')
            remotediff = remotekeys-localkeys
            for remote in remotediff:
                rpath = remotedict[remote]
                remotepath = remotedir + rpath
                filepath = os.path.join(localdir,rpath.replace('/',os.path.sep))
                addfile(remotepath,filepath)
                continue
            if(platform.system() == 'Linux'):
                os.system('chmod 744 %s' % play)
            printf (time.strftime('%Y-%m-%d %H:%M:%S')+'：play由%s版本更新至%s版本成功！' % (ls,rs))
        checksync(projectdir,workdir,'BusSync',play,syncservice)
        checksale(projectdir,workdir,'BusSale',play,port,nginx,ngconf,delay,saleservice)
        time.sleep(60)

def removefile(filepath):
    parentdir = os.path.dirname(filepath)
    try:
        os.remove(filepath)
        printf ('del:%s' % filepath)
    except:
        printf ('already del : %s' % filepath)
    try:
        filelist = os.listdir(parentdir)
        if len(filelist) == 0 :
            try:
                os.rmdir(parentdir)
                printf ('deldir:%s' % parentdir)
            except:
                printf ('already deldir : %s' % parentdir)
    except:
        printf ('%s not exist' % parentdir)

def addfile(remotepath,filepath):
    dirname = os.path.dirname(filepath)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        printf ('mkdir:%s' % dirname)
    try:
        downloadFile(remotepath,filepath)
        printf ('add:%s' % filepath)
    except:
        printf ('failed:%s' % remotepath)

if __name__ == '__main__':
    
    if(platform.system() == 'Linux'):
        cmd = "ps aux|grep %s|awk '{print $2}'" % __file__
        pid = os.getpid()
        for s in os.popen(cmd).readlines():
            if pid != int(s):
                os.popen('kill %d' % int(s))
    
    config = ConfigParser.ConfigParser()
    with open('update.conf') as conf:
        config.readfp(conf)
    UPDATE_CONFIG = config
    
    remotedir = config.get('global','remotedir')
    
    workdir = config.get('global','workdir')
    
    pymdir = os.path.join(workdir,'pym')
    sys.path.append(pymdir)
    
    from pyutil import printf,downloadFile
    from checksync import checksync
    from checksale import checksale
    checkplay(remotedir,workdir)