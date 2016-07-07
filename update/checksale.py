#!/usr/bin/env python
#coding=utf-8

import os
import sys
import time
import urllib2
import shutil
import zipfile
import platform

def checksale(remotedir,localdir,projectname,playpath,port,nginx,ngconf,delay,servicename):
    from pyutil import printf,downloadFile,projectcontroller,projectcontrollerwin
    import updateport,updatelocaldb
    
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

    dbdir = os.path.join(configdir,'localdb')#主sql脚本目录
    patchdir = os.path.join(dbdir,'Patch')#补丁sql脚本目录

    newver = os.path.join(configdir,'version')#升级后的版本文件，取自updateconfig目录
    
    defaultconf = os.path.join(ngconf,'nginx.conf')#默认nginx配置文件
    formalconf = os.path.join(ngconf,'nginx_formal.conf')#正常nginx配置文件，切换回正常环境时使用
    ngtmpconf = os.path.join(ngconf,'nginx_tmp.conf')#临时nginx配置文件，仅端口修改为7890

    rv = ''
    try:
        rv = urllib2.urlopen(rverfile).read()
    except:
        printf ('无法读取%s远程版本文件，请通过浏览器确认文件是否可以访问！等待60秒后尝试下次更新！' % rverfile)
        return

    lv = 'v'
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
            durl = urllib2.urlopen(dfile).read()  #判断是否有 工程名 的文件，读取文件里面写的指向common的路径
        except:
            flag = False
            printf ('Can\'t find %s/%s/%s,direct download zip file!' % (remoteproject,rv.strip(),projectname))

        if os.path.exists(configdir):
            shutil.rmtree(configdir)
        os.makedirs(configdir)

        flag2 = True #flag2为true表示所有下载均正常
        if flag:  #flag为true表示 下载common +特定车站配置文件
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
        else:  #flag为false表示 直接下载 工程.zip
            try:
                downloadFile('%s/%s/%s.zip' % (remoteproject,rv.strip(),projectname),zfile)
            except:
                flag2 = False
                printf ('Can\'t find %s/%s/%s.zip,升级失败！' % (remoteproject,rv.strip(),projectname))

        if flag2:  #flag2为true表示 下载成功
            if os.path.exists(tmpproject):
                shutil.rmtree(tmpproject)  #删除临时工程
            shutil.copytree(localproject,tmpproject)  #COPY旧的工程 到 临时工程
            
            try:
                updateport.modifyconf(tmpconf,'http.port',port)  #修改临时工程的端口
            except:
                printf ('Can\'t modify tmp project port:%s' % tmpconf)
    
            try:
                os.remove(os.path.join(tmpproject,'server.pid'))
            except:
                pass
    
            projectcontroller(playpath,'start',tmpproject) #启动临时工程
            
            shutil.copyfile(ngtmpconf,defaultconf) #COPY临时工程NGINX配置为当前配置
            os.chdir(os.path.dirname(nginx)) #切换当前目录到NGINX目录
            os.system('%s -s reload' % nginx) #平滑切换NGINX到临时工程
            
            time.sleep(delay)  
            
            if(platform.system() == 'Linux'):
                projectcontroller(playpath,'stop',localproject)
            else:
                projectcontrollerwin('stop',servicename)
    
            shutil.rmtree(localproject) #删除正式工程
    
            f = zipfile.ZipFile(zfile)
            f.extractall(localdir) #解压下载工程.zip 到正式工程
    
            if os.path.exists(stationconf): #如果存在车站分离配置文件（有可能是单独下载的，也有可能是解压的）
                appcf = open(localconf,'a+')
                stcf = open(stationconf).read()
                appcf.write(os.linesep)
                appcf.write(stcf)
                appcf.close()
    
            if os.path.exists(slog4jprop): #如果存在车站分离配置文件（有可能是单独下载的，也有可能是解压的）
                logcf = open(localprop,'a+')
                stscf = open(slog4jprop).read()
                logcf.write(os.linesep)
                logcf.write(stscf)
                logcf.close()
    
            updatelocaldb.execsql(localconf,dbdir,patchdir)
    
            if os.path.exists(newver):  #更新当前版本文件
                shutil.copy(newver,localproject)
    
            if(platform.system() == 'Linux'):
                projectcontroller(playpath,'start',localproject)
            else:
                projectcontrollerwin('start',servicename)
            
            shutil.copyfile(formalconf,defaultconf)  #COPY正式工程NGINX配置为当前配置
            os.chdir(os.path.dirname(nginx))
            os.system('%s -s reload' % nginx) #平滑切换NGINX到正式工程

            time.sleep(delay)
                
            projectcontroller(playpath,'stop',tmpproject)
    
            printf (time.strftime('%Y-%m-%d %H:%M:%S')+' %s由%s版本更新至%s版本成功！' % (projectname,lv[:-1],rv))
