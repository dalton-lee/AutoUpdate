#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
import shutil
import platform

if __name__=="__main__":
    
    if(platform.system() == 'Linux'):
#        shutil.move('/home/lee/pym', '/home/lee/pymbak')
#        shutil.copytree(os.getcwd(),"/home/lee/pym")
        appconf = codecs.open('/home/lee/BusSale/conf/application.conf', 'r', 'utf-8')
    else:
#        shutil.move('D:\\lee\\pym', 'D:\\lee\\pymbak')
#        shutil.copytree(os.getcwd(),"D:\\lee\\pym")
        appconf = codecs.open('D:\\lee\\BusSale\\conf\\application.conf', 'r', 'utf-8')

    for line in appconf.readlines():
        if not line:
            continue
        if line.strip().startswith("#"):
            continue
        if line.find('=') > 0 and line.find('station.orgcode') > -1:
            orgline = line.strip()
            orgindex = orgline.index('=')
            orgcode = orgline[orgindex+1:len(orgline)].strip()

    content = '[global]' + os.linesep
    
    if(platform.system() == 'Linux'):
        workdir = 'workdir=/home/lee' + os.linesep
    else:
        workdir = 'workdir=D:\\lee' + os.linesep
    
    orgcode = 'orgcode=' + orgcode + os.linesep
    
    content = content + workdir + orgcode + os.linesep
    
    content = content + '[BusSync]' + os.linesep
    
    content = content + '[BusSale]' + os.linesep
    
    port = 'port=7890' + os.linesep
    
    if(platform.system() == 'Linux'):
        nginx = 'nginx=/usr/sbin/nginx' + os.linesep
        ngconf = 'ngconf=/etc/nginx' + os.linesep
    else:
        nginx = 'nginx=D:\\lee\\nginx-1.5.12\\nginx' + os.linesep
        ngconf = 'ngconf=D:\\lee\\nginx-1.5.12\\conf' + os.linesep
    
    delay = 'delay=60' + os.linesep
    
    content = content + port + nginx + ngconf + delay
    
    if(platform.system() == 'Linux'):
        updateconf = codecs.open('/home/lee/pym/update.conf', 'w', 'utf-8')
    else:
        updateconf = codecs.open('D:\\lee\\pym\\update.conf', 'w', 'utf-8')
    
    updateconf.write(content)
    
    updateconf.close()