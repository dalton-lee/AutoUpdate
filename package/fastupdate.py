#!/usr/bin/env python
#coding=utf-8
'''
Created on 2015年6月25日

@author: lidongcheng@lee.com
'''

import os
import sys
import time
import shutil
import zipfile
import platform
import ConfigParser

UPDATE_CONFIG = 0

def sync(workdir,playpath,codedir,projectname):
    
    versionfile = os.path.join(codedir,projectname,'version')
    
    try:
        version = open(versionfile).read()
    except:
        printf ('Can\'t find version file:%s' % versionfile)
        
    zfile = os.path.join(codedir,projectname,version,'%s.zip' % projectname)
    
    localproject = os.path.join(workdir,projectname)
    
    localconf = os.path.join(localproject,'conf','application.conf')
    
    configdir = os.path.join(workdir,'updateconfig')
    
    dbdir = os.path.join(configdir,'localdb')
    patchdir = os.path.join(dbdir,'Patch')
    
    newver = os.path.join(configdir,'version')
    
    if not os.path.isdir(localproject):
        os.makedirs(localproject)
    
    if(platform.system() == 'Linux'):
        projectcontroller(playpath,'stop',localproject)
    else:
        projectcontrollerwin('stop','%sService' % projectname)
        
    shutil.rmtree(localproject)

    f = zipfile.ZipFile(zfile)
    f.extractall(workdir)
    
    updatelocaldb.execsql(localconf,dbdir,patchdir)

    if os.path.exists(newver):
        shutil.copy(newver,localproject)
    if(platform.system() == 'Linux'):
        projectcontroller(playpath,'start',localproject)
    else:
        projectcontrollerwin('start','%sService' % projectname)
    printf (time.strftime('%Y-%m-%d %H:%M:%S')+'：%s更新成功！' % projectname)
    
    
def sale(workdir,playpath,port,nginx,ngconf,delay,codedir):
    
    versionfile = os.path.join(codedir,'BusSale','version')
    
    try:
        version = open(versionfile).read()
    except:
        printf ('Can\'t find version file:%s' % versionfile)
        
    zfile = os.path.join(codedir,'BusSale',version,'BusSale.zip')
    
    localproject = os.path.join(workdir,'BusSale')
    
    tmpproject = '%s%s' % (localproject,'tmp')
    
    localconf = os.path.join(localproject,'conf','application.conf')
    
    tmpconf = os.path.join(tmpproject,'conf','application.conf')
    
    configdir = os.path.join(workdir,'updateconfig')
    
    dbdir = os.path.join(configdir,'localdb')
    patchdir = os.path.join(dbdir,'Patch')
    
    newver = os.path.join(configdir,'version')
    
    defaultconf = os.path.join(ngconf,'nginx.conf')
    formalconf = os.path.join(ngconf,'nginx_formal.conf')
    ngtmpconf = os.path.join(ngconf,'nginx_tmp.conf')

    if os.path.exists(tmpproject):
        shutil.rmtree(tmpproject)
        
    shutil.copytree(localproject,tmpproject)
    
    try:
        updateport.modifyconf(tmpconf,'http.port',port)
    except:
        printf ('Can\'t modify tmp project port:%s' % tmpconf)

    try:
        os.remove(os.path.join(tmpproject,'server.pid'))
    except:
        pass

    projectcontroller(playpath,'start',tmpproject)
    
    shutil.copyfile(ngtmpconf,defaultconf)
    os.chdir(os.path.dirname(nginx))
    os.system('%s -s reload' % nginx)
    
    time.sleep(delay)  
    
    if(platform.system() == 'Linux'):
        projectcontroller(playpath,'stop',localproject)
    else:
        projectcontrollerwin('stop','BusSaleService')

    shutil.rmtree(localproject)

    f = zipfile.ZipFile(zfile)
    f.extractall(workdir)

    updatelocaldb.execsql(localconf,dbdir,patchdir)

    if os.path.exists(newver):
        shutil.copy(newver,localproject)

    if(platform.system() == 'Linux'):
        projectcontroller(playpath,'start',localproject)
    else:
        projectcontrollerwin('start','BusSaleService')
    
    shutil.copyfile(formalconf,defaultconf)
    os.chdir(os.path.dirname(nginx))
    os.system('%s -s reload' % nginx)

    time.sleep(delay)
        
    projectcontroller(playpath,'stop',tmpproject)

    printf (time.strftime('%Y-%m-%d %H:%M:%S')+'：BusSale更新成功！')


def updateconfig():
    
    from pyutil import printf
    
    config = ConfigParser.ConfigParser()
    
    try:
        updateconf = open('/home/lee/pym/update.conf')
    except:
        try:
            updateconf = open('D:\\lee\\pym\\update.conf')
        except:
            try:
                updateconf = open('update.conf')
            except:
                printf ('找不到update.conf文件,升级程序异常退出，请检查后重试！')
                sys.exit()
    
    config.readfp(updateconf)
    UPDATE_CONFIG = config

def syncmod(projectname):
    from pyutil import printf,projectcontroller,projectcontrollerwin
    import updatelocaldb
    
    updateconfig()
    
    global UPDATE_CONFIG
    
    workdir = UPDATE_CONFIG.get('global','workdir')
    
    pymdir = os.path.join(workdir,'pym')
    sys.path.append(pymdir)
    
    playpath = os.path.join(workdir,'play-1.2.3','play')
    
    orgcode = UPDATE_CONFIG.get('global','orgcode')
    
    codedir = os.path.join(workdir,orgcode)
    
    sync(workdir,playpath,codedir,projectname)

def salemod():
    from pyutil import printf,projectcontroller,projectcontrollerwin
    import updatelocaldb,updateport
    
    updateconfig()
    
    global UPDATE_CONFIG
    
    workdir = UPDATE_CONFIG.get('global','workdir')
    
    pymdir = os.path.join(workdir,'pym')
    sys.path.append(pymdir)
    
    playpath = os.path.join(workdir,'play-1.2.3','play')
    
    port = UPDATE_CONFIG.get('BusSale','port')
    
    nginx = UPDATE_CONFIG.get('BusSale', 'nginx')
    
    ngconf = UPDATE_CONFIG.get('BusSale', 'ngconf')
    
    delay = UPDATE_CONFIG.get('BusSale', 'delay')
    delay = float(delay)
    
    orgcode = UPDATE_CONFIG.get('global','orgcode')
    
    codedir = os.path.join(workdir,orgcode)
    
    sale(workdir,playpath,port,nginx,ngconf,delay,codedir)
    

#if __name__=='__main__':
#---------------------------------------分 割 线--------------------------------------------------
#一下内容仅供测试使用
def mainfunction():
    from pyutil import printf,projectcontroller,projectcontrollerwin
    import updatelocaldb,updateport
    
    config = ConfigParser.ConfigParser()
    
    try:
        updateconf = open('/home/lee/pym/update.conf')
    except:
        try:
            updateconf = open('D:\\lee\\pym\\update.conf')
        except:
            try:
                updateconf = open('update.conf')
            except:
                printf ('找不到update.conf文件,升级程序异常退出，请检查后重试！')
                sys.exit()
    
    config.readfp(updateconf)
    
    workdir = config.get('global','workdir')
    
    pymdir = os.path.join(workdir,'pym')
    sys.path.append(pymdir)
    
    playpath = os.path.join(workdir,'play-1.2.3','play')
    
    port = config.get('BusSale','port')
    
    nginx = config.get('BusSale', 'nginx')
    
    ngconf = config.get('BusSale', 'ngconf')
    
    delay = config.get('BusSale', 'delay')
    delay = float(delay)
    
    orgcode = config.get('global','orgcode')
    
    codedir = os.path.join(workdir,orgcode)
    
    projectname = 'BusSync'
    sync(workdir,playpath,codedir,projectname)
        
    sale(workdir,playpath,port,nginx,ngconf,delay,codedir)