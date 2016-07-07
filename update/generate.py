#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import codecs
import shutil

if __name__=="__main__":
    
    shutil.move('/home/lee/pym', '/home/lee/pymbak')
    
    shutil.copytree(sys.path[0],"/home/lee/pym")
    
    appconf = codecs.open('/home/lee/BusSync/conf/application.conf', 'r', 'utf-8')
#    appconf = codecs.open(r'F:\project\bj_1310_zwjk\Branches\v2.7\SRC\BusSale\plugin\jzxx\application.conf', 'r', 'utf-8')
    
    for line in appconf.readlines():
        if not line:
            continue
        if line.strip().startswith("#"):
            continue
        if line.find('=') > 0 and line.find('station.orgcode') > -1:
            orgline = line.strip()
            orgindex = orgline.index('=')
            orgcode = orgline[orgindex+1:len(orgline)].strip()
        if line.find('=') > 0 and line.find('openapiUrl') > -1:
            apiline = line.strip()
            apiindex = apiline.index('=')
            openapiUrl = apiline[apiindex+1:len(apiline)].strip()
    
    updateconf = codecs.open('/home/lee/pym/update.conf', 'w', 'utf-8')
    
    content = '[global]' + os.linesep
    
    try:
        openapiUrl = '192.168.3.66:9011'
        remotedir = 'remotedir=http://' + openapiUrl + '/takepackage/' + os.linesep
    except NameError:
        print 'Can\'t find variable <openapiUrl>,script terminate!'
        os._exit(1)
    
    localdir = 'localdir=/home/lee' + os.linesep
    
    try:
        orgcode = 'orgcode=' + orgcode + os.linesep
    except NameError:
        print 'Can\'t find variable <orgcode>,script terminate!'
        os._exit(1)
    
    content = content + remotedir + localdir + orgcode + os.linesep
    
    content = content + '[BusSync]' + os.linesep
    
    syncservice = 'servicename=BusSyncService' + os.linesep
    
    content = content + syncservice + os.linesep
    
    content = content + '[BusSale]' + os.linesep
    
    port = 'port=7890' + os.linesep
    
    nginx = 'nginx=/usr/sbin/nginx' + os.linesep
    
    comment = '#nginx配置项为具体可执行文件，而ngconf的值为配置文件的目录'.decode('utf-8') + os.linesep
    
    ngconf = 'ngconf=/etc/nginx' + os.linesep
    
    delay = 'delay=60' + os.linesep
    
    saleservice = 'servicename=BusSaleService' + os.linesep
    
    content = content + port + nginx + comment + ngconf + delay + saleservice
    
    updateconf.write(content)
    
    updateconf.close()