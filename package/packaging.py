#!/usr/bin/env python
#-*-coding:utf-8-*-

import os
import chardet
import codecs
import ConfigParser
import zipfile
import pysvn
import datetime
import platform
import shutil

GLOBAL_CONFIG = 0

def getConfig(filename):
    global GLOBAL_CONFIG
    fileencode = chardet.detect(codecs.open(filename).read())['encoding']
    fp = codecs.open(filename,'r',fileencode)
#    fp = codecs.open(filename,'r','utf-8')
#    data = fp.read()
#    if data[:3] == codecs.BOM_UTF8:
#        data = data[3:]
    config = ConfigParser.ConfigParser()
    config.readfp(fp)
    fp.close()
    GLOBAL_CONFIG = config

def getValue(sectionName,optionName):
    global GLOBAL_CONFIG
    if not GLOBAL_CONFIG.has_section(sectionName):
        printf(u'配置文件中不存在 %s这个section!' % sectionName)
        return None
    if GLOBAL_CONFIG.has_option(sectionName,optionName):
        return GLOBAL_CONFIG.get(sectionName,optionName)
    else:
        printf(u'配置文件中%s这个section下未找到名为%s的option' % (sectionName,optionName))
        return None

def compress(dirname,zipfilename):
    filelist = []
    for dirpath, subdirs, filenames in os.walk(dirname):
        for filaname in filenames:
            filelist.append(os.path.join(dirpath, filaname))
    zipfp = zipfile.ZipFile(zipfilename, 'w' ,zipfile.ZIP_DEFLATED)
    for filepath in filelist:
        arcname = filepath[len(dirname):]
        zipfp.write(filepath,arcname)
    zipfp.close()

def get_login(realm, username, may_save):
    username = getValue('Authority certification','username')
    password = getValue('Authority certification','password')
    retcode = getValue('Authority certification','retcode')
    save = getValue('Authority certification','save')
    return retcode, username, password, save

client = pysvn.Client()
client.callback_get_login = get_login

def takepackage(project,version,stationnameuni):
    tarversion = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    tarversion = version + '_' + tarversion
    
    svnpath = getValue(project,'svnpath')
    archivedir = getValue(project,'archivepath')

    stationcode = getValue('stationcode',stationnameuni)
    pluginname = getValue('plugin',stationnameuni)

    versiondir = os.path.join(archivedir,stationcode,project,tarversion)

    folderlist = getValue(project,'folderlist')
    folders = folderlist.split(',')
    
    for folder in folders:
        remotepath = svnpath+'/Branches/'+version+'/SRC/'+project+'/'+folder
        localpath = os.path.join(versiondir,project,folder)
        client.export(remotepath,localpath)
    
    confpath = os.path.join(versiondir,project,'conf')

    if os.path.isfile(os.path.join(confpath,'application.conf')):
        os.remove(os.path.join(confpath,'application.conf'))
        
    if os.path.isfile(os.path.join(confpath,'log4j.properties')):   
        os.remove(os.path.join(confpath,'log4j.properties'))


#   ----批量注释原下载公共配置文件及车站独立配置文件，再进行合并的代码
#     pubconfpath = svnpath+'/Trunk/SRC/takepackage/publicconfig/'+project+'/application.conf'
#     client.export(pubconfpath,confpath)
#
#     pubproppath = svnpath+'/Trunk/SRC/takepackage/publicconfig/'+project+'/log4j.properties'
#     client.export(pubproppath,confpath)
#
#     staconfpath = svnpath+'/Branches/'+version+'/SRC/'+project+'/plugin/'+pluginname+'/station_%s.conf' % stationnameuni
#     client.export(staconfpath,confpath)
#
#     staproppath = svnpath+'/Branches/'+version+'/SRC/'+project+'/plugin/'+pluginname+'/stationlog4j_%s.properties' % stationnameuni
#     client.export(staproppath,confpath)
#
#     pubconfprop = getProperties(os.path.join(confpath,'application.conf'))
#     plugconfprop = getProperties(os.path.join(confpath,'station_%s.conf' % stationnameuni))
#     mergePropertiesToFile(pubconfprop,plugconfprop,os.path.join(confpath,'application.conf'))
#     os.remove(os.path.join(confpath,'station_%s.conf' % stationnameuni))
#
#     publogprop = getProperties(os.path.join(confpath,'log4j.properties'))
#     pluglogprop = getProperties(os.path.join(confpath,'stationlog4j_%s.properties' % stationnameuni))
#     mergePropertiesToFile(publogprop,pluglogprop,os.path.join(confpath,'log4j.properties'))
#     os.remove(os.path.join(confpath,'stationlog4j_%s.properties' % stationnameuni))
#   -----批量注释原下载公共配置文件及车站独立配置文件，再进行合并的代码


#   直接下载车站生产环境的配置文件
    pzdir = u'配置文件'
    station_application = 'svn://192.168.3.3/interfaceconfig/%s/%s/%s/conf/application.conf'  % (pzdir,stationnameuni,project)
    client.export(station_application,confpath)
    station_log4j = 'svn://192.168.3.3/interfaceconfig/%s/%s/%s/conf/log4j.properties'  % (pzdir,stationnameuni,project)
    client.export(station_log4j,confpath)

    svnplugin = svnpath+'/Branches/'+version+'/SRC/'+project+'/plugin/'+pluginname+'/app'
    localplugin = os.path.join(versiondir,project,'plugin',pluginname,'app')
    client.export(svnplugin,localplugin)
    
    svnsqlpath = svnpath+'/Branches/'+version+'/SQL/'+version.replace("v","V")+'/sil'
    localdb = os.path.join(versiondir,'updateconfig','localdb')
    client.export(svnsqlpath,localdb)

#    svnpatchpath = svnpath+'/Branches/'+version+'/SQL/Patch/sil'
#    patchpath = os.path.join(versiondir,'updateconfig','localdb','Patch')
#    client.export(svnpatchpath,patchpath)

    versionfile = os.path.join(versiondir,'updateconfig','version')
    f = codecs.open(versionfile,'w','utf-8')
    f.write(tarversion)
    f.close()
    

    compress(versiondir,os.path.join(versiondir,'%s.zip' % project))
    
    shutil.copy(versionfile, os.path.join(os.path.dirname(versiondir),'version'))
    
    shutil.rmtree(os.path.join(versiondir,project))
    shutil.rmtree(os.path.join(versiondir,'updateconfig'))
        
def getProperties(filename):
    fileencode = chardet.detect(codecs.open(filename).read())['encoding']
    p = codecs.open(filename,'r',fileencode)
    properties = {}
    for line in p.readlines():
        if not line:
            continue
        if line.strip().startswith("#"):
            continue
        if line.find('=') > 0:
            if fileencode.lower() == 'utf-8':
                if line.encode('utf-8')[:3] == codecs.BOM_UTF8:
                    line = line.encode('utf-8')[3:].decode('utf-8')
            strs = line.strip()
            index = strs.index('=')
            properties[strs[0:index].strip()] = strs[index+1:len(strs)].strip()
    p.close()
    return properties

def mergePropertiesToFile(p1,p2,filename):  #注意p2中的属性值会覆盖p1中的同名属性值
    p = codecs.open(filename,'w','utf-8')
    p1.update(p2)
    items = p1.items()
    items.sort()
    for key,value in items:
        p.write(key+'='+value)
        p.write(os.linesep)
    p.close()
    
def printf(string):
    if(platform.system() != 'Windows'):
        print(string)
    else:
#        print(string.decode('utf-8').encode('gbk'))
        print(string)

if __name__=="__main__":
    getConfig(r'packaging.ini')
    optins = GLOBAL_CONFIG.options('plugin')
    syncversion = GLOBAL_CONFIG.get('BusSync','version')
    saleversion = GLOBAL_CONFIG.get('BusSale','version')
    syncerror = []
    saleerror = []
    
    printf(u'请输入打包方式：1.单个工程；2.打包所有工程：')
    flag = raw_input()
    
    if flag == '1':
        printf(u'请输入工程名:')
        project = raw_input()
        
        printf(u'请输入分支版本号:')
        version = raw_input()
        
        printf(u'请输入车站名称:')
        station = raw_input()
        printf('input:'+station)
        print platform.system()
        if(platform.system() != 'Windows'):
            stationuni = station
        else:
            stationuni = station.decode('gbk')
        printf('stationuni:'+station)
        takepackage(project,version,stationuni)
        
    elif flag == '2':
        printf(u'开始打包：%s' % datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        for key in optins:
            try:
                takepackage('BusSync',syncversion,key)
            except:
                syncerror.append(key)
            try:
                takepackage('BusSale',saleversion,key)
            except:
                saleerror.append(key)
        printf(u'打包结束：%s' % datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
        printf(u'同步打包异常车站：')
        for sy in syncerror:
            print sy
        printf(u'业务打包异常车站：')
        for sa in saleerror:
            print sa
    else:
        printf(u'参数输入错误！')