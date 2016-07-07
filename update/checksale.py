#!/usr/bin/env python
#coding=utf-8

import os
import sys
import time
import urllib2

sys.path.append('/home/lee/pym')
import updateport

def checksale(projecthost,localproject,tofile,playpath,changeurl,port):
    if not os.path.isdir(localproject):
        os.mkdir(localproject)
    versionurl = os.path.join(projecthost,'version')
    versionfile = os.path.join(localproject,'version')
    tmpproject = '%s%s' % (localproject,'tmp')
    localconf = os.path.join(localproject,'conf/application.conf')
    tmpconf = os.path.join(tmpproject,'conf/application.conf')
    localprop = os.path.join(localproject,'conf/log4j.properties')
    while(True):
        rv = ''
        try:
            rv = urllib2.urlopen(versionurl).read()
        except:
            print 'Connection refused: %s' % versionurl

        lv = 'v'
        try:
            lv = open(versionfile).read()
        except:
            print 'Can\'t find versionfile:%s' % versionfile

        if rv.strip() == lv.strip() :
            print time.strftime('%Y-%m-%d %H:%M:%S')+' 暂无更新，当前版本号为：%s' % rv
        else:
            os.system('cp -rf %s %s' % (localproject,tmpproject))
            try:
                updateport.modifyconf(tmpconf,'http.port',port)
            except:
                print 'Can\'t modify tmp project port:%s' % versionfile
            try:
                os.remove(os.path.join(tmpproject,'server.pid'))
            except:
                pass
            action(playpath,'start',tmpproject)
            nport = '9000';
            try:
                nport = updateport.getport(localconf,'http.port')
            except:
                print 'Can\'t find localconf:%s' % localconf
            status = 'true'#tmp
#            try:
#                status = urllib2.urlopen('%s&port=%s' % (changeurl,port)).read()
#            except:
#                print 'chang port Connection refused :%s&port=%s' % (changeurl,port)
#                time.sleep(60)
            if 'true'==status:
                action(playpath,'stop',localproject)
                try:
                    downloadFile('%s/%s/BusSale.zip' % (projecthost,rv.strip()),tofile)
                except:
                    print 'not found %s/%s/BusSale.zip' % (projecthost,rv.strip())
                    time.sleep(60)
                    continue
                os.system('rm -rf /home/lee/updateconfig')
                os.system('rm -rf %s' % localproject)
                os.system('unzip -oq %s -d /home/lee/' % tofile)
                if os.path.exists('/home/lee/updateconfig/station.conf'):
                    appcf = open(localconf,'a+')
                    stcf = open('/home/lee/updateconfig/station.conf').read()
                    appcf.write(stcf)
                    stcf.close()
                    appcf.close()
                if os.path.exists('/home/lee/updateconfig/stationlog4j.properties'):
                    logcf = open(localprop,'a+')
                    stscf = open('/home/lee/updateconfig/stationlog4j.properties').read()
                    logcf.write(stcf)
                    stscf.close()
                    logcf.close()
                os.system('python /home/lee/pym/updatelocaldb.py')
                if os.path.exists('/home/lee/updateconfig/version'):
                    os.system('cp /home/lee/updateconfig/version %s' % localproject)
                action(playpath,'start',localproject)
#                status = ''
#                try:
#                    status = urllib2.urlopen('%s&port=%s' % (changeurl,nport)).read()
#                except:
#                    print 'rollback port failure'
#                if 'true'==status:
                action(playpath,'stop',tmpproject)
 #               else:
#                    print 'can not stop tmpproject'
            else:
                print 'change port failure'
            print time.strftime('%Y-%m-%d %H:%M:%S')+' 由%s版本更新至%s版本成功！' % (lv[:-1],rv)
        time.sleep(10)

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
    projecthost = 'http://192.168.3.66:8080/takepackage/22010000005/BusSale/'
    localproject = '/home/lee/BusSale'
    tofile = '/home/lee/BusSale.zip'
    playpath = '/home/lee/play-1.2.3/play'
    changeurl = 'http://192.168.3.66:9002/updateport?orgcode=150100TCZ&updataclass=SERVERSADDRESS'
    port = '7890'
    checksale(projecthost,localproject,tofile,playpath,changeurl,port)
