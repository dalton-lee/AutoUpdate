#!/usr/bin/env python
#coding=utf-8

import os
import sys
import time
import urllib2
import shutil
import zipfile
import platform

def checksale(remotedir,localdir,projectname,playpath,port,nginx,ngconf):
    pymdir = os.path.join(localdir,'pym')#自定义python模块目录
    sys.path.append(pymdir)
    import updateport
    
    localproject = os.path.join(localdir,projectname)#本地工程目录
    tmpproject = '%s%s' % (localproject,'tmp')#临时工程目录

    if not os.path.isdir(localproject):
        os.makedirs(localproject)

    if not remotedir.endswith('/'):
        remoteproject = remotedir + '/' + projectname
    else:
        remoteproject = remotedir + projectname

    lverfile = os.path.join(localproject,'version')#本地版本文件
    rverfile = remoteproject + '/version'#远程版本文件

    zfile = os.path.join(localdir,'%s.zip' % projectname)#升级时下载的zip文件
    configdir = os.path.join(localdir,'updateconfig')#解压后的配置文件目录

    localconf = os.path.join(localproject,'conf','application.conf')#合并前的配置文件
    stationconf = os.path.join(configdir,'station.conf')#合并前插件对应的车站conf文件
    tmpconf = os.path.join(tmpproject,'conf','application.conf')#临时工程的配置文件，修改端口用

    localprop = os.path.join(localproject,'conf','log4j.properties')#合并前的log4j.properties
    slog4jprop = os.path.join(configdir,'stationlog4j.properties')#合并前插件对应的车站log4j文件

    dbexec = os.path.join(pymdir,'updatelocaldb.py')#自定义的sql脚本执行文件
    playdir = os.path.dirname(playpath)#play根目录，windows下需要使用其内置的python

    newver = os.path.join(configdir,'version')#升级后的版本文件，取自updateconfig目录
    
    defaultconf = os.path.join(ngconf,'nginx.conf')#默认nginx配置文件
    formalconf = os.path.join(ngconf,'nginx_formal.conf')#正常nginx配置文件，切换回正常环境时使用
    ngtmpconf = os.path.join(ngconf,'nginx_tmp.conf')#临时nginx配置文件，仅端口修改为7890

    while(True):
        rv = ''
        try:
            rv = urllib2.urlopen(rverfile).read()
        except:
            print 'Connection refused: %s' % rverfile

        lv = 'v'
        try:
            lv = open(lverfile).read()
        except:
            print 'Can\'t find versionfile:%s' % lverfile

        if rv.strip() == lv.strip() :
            print time.strftime('%Y-%m-%d %H:%M:%S')+' 暂无更新，当前版本号为：%s' % rv
        else:
            shutil.rmtree(tmpproject)
            shutil.copytree(localproject,tmpproject)
            
            try:
                updateport.modifyconf(tmpconf,'http.port',port)
            except:
                print 'Can\'t modify tmp project port:%s' % tmpconf

            try:
                os.remove(os.path.join(tmpproject,'server.pid'))
            except:
                pass

            action(playpath,'start',tmpproject)
            
            shutil.copyfile(ngtmpconf,defaultconf)
            os.system('% -s reload' % nginx)
            
            action(playpath,'stop',localproject)

            try:
                downloadFile('%s/%s/%s.zip' % (remoteproject,rv.strip(),projectname),zfile)
            except:
                print 'not found %s/%s/%s.zip' % (localproject,rv.strip(),projectname)
                time.sleep(60)
                continue

            if os.path.exists(configdir):
                shutil.rmtree(configdir)
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
                pyrt = os.path.join(playdir,'python','python.exe')
                os.system('%s %s' % (pyrt,dbexec))
            else:
                os.system(dbexec)

            if os.path.exists(newver):
                shutil.copy(newver,localproject)

            action(playpath,'start',localproject)

            shutil.copyfile(formalconf,defaultconf)
            os.system('% -s reload' % nginx)

            action(playpath,'stop',tmpproject)

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
    projectname = 'BusSale'
    playpath = '/home/lee/play-1.2.3/play'#可执行文件
#    Window下，此文件为D:\lee\play-1.2.3\play.bat
    port = '7890'
    nginx = '/usr/sbin/nginx'#可执行文件
    ngconf = '/etc/nginx'#配置文件目录
    checksale(remotedir,localdir,projectname,playpath,port,nginx,ngconf)