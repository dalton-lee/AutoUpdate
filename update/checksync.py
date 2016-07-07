#!/usr/bin/env python
#coding=utf-8

import os
import sys
import time
import shutil
import zipfile
import urllib2
import platform

def checksync(remotedir,localdir,projectname,playpath):
    pymdir = os.path.join(localdir,'pym')
    sys.path.append(pymdir)
    from pyutil import printf,downloadFile,projectcontroller

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
    
    dbexec = os.path.join(pymdir,'updatelocaldb.py')
    
    localconf = os.path.join(localproject,'conf','application.conf')
    stationconf = os.path.join(configdir,'station.conf')
    
    localprop = os.path.join(localproject,'conf','log4j.properties')
    slog4jprop = os.path.join(configdir,'stationlog4j.properties')
    
    newver = os.path.join(configdir,'version')
    
    rv = '1'
    try:
        rv = urllib2.urlopen(rverfile).read()
    except:
        printf ('Connection refused: %s' % rverfile)

    lv = '0'
    try:
        lv = open(lverfile).read()
    except:
        printf ('Can\'t find local version file:%s' % lverfile)

    if rv.strip() == lv.strip() :
        printf (time.strftime('%Y-%m-%d %H:%M:%S')+'：%s暂无更新，当前版本号为：%s' % (projectname,rv))
    else:
        flag = True
        try:
            downloadFile('%s/%s/%s.zip' % (remoteproject,rv.strip(),projectname),zfile)
        except:
            flag = False
            printf ('Can\'t found %s/%s/%s.zip' % (remoteproject,rv.strip(),projectname))
        if flag:
            if os.path.exists(configdir):
                shutil.rmtree(configdir)
    
            projectcontroller(playpath,'stop',localproject)
            shutil.rmtree(localproject)
    
            f = zipfile.ZipFile(zfile)
            f.extractall(localdir)
            
            if os.path.exists(stationconf):
                appcf = open(localconf,'a+')
                stcf = open(stationconf).read()
                appcf.write(stcf)
                appcf.close()
    
            if os.path.exists(slog4jprop):
                logcf = open(localprop,'a+')
                stscf = open(slog4jprop).read()
                logcf.write(stscf)
                logcf.close()
    
            if(platform.system() == 'Windows'):
                playdir = os.path.dirname(playpath)
                pyrt = os.path.join(playdir,'python','python.exe')
                os.system('%s %s' % (pyrt,dbexec))
            else:
                os.system('python %s' % dbexec)
    
            if os.path.exists(newver):
                shutil.copy(newver,localproject)
    
            projectcontroller(playpath,'start',localproject)
            printf (time.strftime('%Y-%m-%d %H:%M:%S')+'：%s由%s版本更新至%s版本成功！' % (projectname,lv[:-1],rv))

def checksyncmod():
    remotedir = 'http://192.168.3.66:8080/takepackage/22010000005'
    localdir = '/home/lee'
    projectname = 'BusSync'
    playpath = '/home/lee/play-1.2.3/play'
    checksync(remotedir,localdir,projectname,playpath)