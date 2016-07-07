#!/usr/bin/env python
#coding=utf-8

'''
Created on 2015年7月15日

@author: Lee
'''

import os

if __name__ == '__main__':
    
    filepath = 'D:\\models\\mm\\lease.sql'
    
    str = ''
    
    for line in open(filepath).readlines():
    
        if(line.upper().find('DROP TABLE')<0):
            
            if(line.upper().find('CREATE TABLE')>-1):
                str = str + line[0:13] + ' IF NOT EXISTS ' + line[13:]
            elif(line.upper().find('INSERT INTO')>-1):
                
                tableindx = line.upper().find('VALUES')
                tablecolumn =  line[12:tableindx].strip()
                
                if(tablecolumn.find('(')>-1):
                    tablecolumn = tablecolumn[:tablecolumn.find('(')]
                
                idindx = line.upper().find('VALUES (')
                index = line.upper().find(',',idindx)
                
                idvalue =  line[idindx+8:index].strip()
                
                sql = '@repeat{select count(*) from ' + tablecolumn + ' where id=' + idvalue + '}\n'
                
                str = str + sql + line
#                str = str + line
            else:
                str = str + line
                
    print str
    
    sqlfile = 'D:\\models\\mm\\lease2.sql'
    
    f = open(sqlfile,'w')
    f.write(str)
    f.close()