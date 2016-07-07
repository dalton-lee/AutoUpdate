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
    from pyutil import printf,downloadFile,projectcontroller
    import updatelocaldb

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
    
    dbdir = os.path.join(configdir,'localdb')#主sql脚本目录
    patchdir = os.path.join(dbdir,'Patch')#补丁sql脚本目录
    
    localconf = os.path.join(localproject,'conf','application.conf')
    stationconf = os.path.join(configdir,'station.conf')
    
    localprop = os.path.join(localproject,'conf','log4j.properties')
    slog4jprop = os.path.join(configdir,'stationlog4j.properties')
    
    newver = os.path.join(configdir,'version')
    
    rv = '1'
    try:
        rv = urllib2.urlopen(rverfile).read()
    except:
        printf ('无法读取%s远程版本文件，请通过浏览器确认文件是否可以访问！等待60秒后尝试下次更新！' % rverfile)
        return

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
            dfile = '%s/%s/%s' % (remoteproject,rv.strip(),projectname)
            durl = urllib2.urlopen(dfile).read()
        except:
            flag = False
            printf ('Can\'t find %s/%s/%s,direct download zip file!' % (remoteproject,rv.strip(),projectname))

        if os.path.exists(configdir):
            shutil.rmtree(configdir)
        os.makedirs(configdir)

        flag2 = True
        if flag:
            try:
                downloadFile('%s/%s/station.conf' % (remoteproject,rv.strip()),stationconf)
                downloadFile('%s/%s/stationlog4j.properties' % (remoteproject,rv.strip()),slog4jprop)
            except:
                flag2 = False
                printf ('Can\'t find %s/%s/station.conf or stationlog4j.properties,update abort!' % (remoteproject,rv.strip()))
            
            try:
                downloadFile(durl,zfile)
            except:
                flag2 = False
                printf ('Can\'t find %s,update abort' % durl)
        else:
            try:
                downloadFile('%s/%s/%s.zip' % (remoteproject,rv.strip(),projectname),zfile)
            except:
                flag2 = False
                printf ('Can\'t find %s/%s/%s.zip' % (remoteproject,rv.strip(),projectname))

        if flag2:
            projectcontroller(playpath,'stop',localproject)
            shutil.rmtree(localproject)
    
            f = zipfile.ZipFile(zfile)
            f.extractall(localdir)
            
            if os.path.exists(stationconf):
                appcf = open(localconf,'a+')
                stcf = open(stationconf).read()
                appcf.write(os.linesep)
                appcf.write(stcf)
                appcf.close()
    
            if os.path.exists(slog4jprop):
                logcf = open(localprop,'a+')
                stscf = open(slog4jprop).read()
                logcf.write(os.linesep)
                logcf.write(stscf)
                logcf.close()
    
            updatelocaldb.execsql(localconf,dbdir,patchdir)
    
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