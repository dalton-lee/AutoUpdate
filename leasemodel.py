#!/usr/bin/env python
#coding=utf-8

'''
Created on 2015年6月26日

@author: Lee
'''

import os
import ConfigParser
import MySQLdb
      
def metacolumn(idnum):
    modeldir = 'D:\\models'
    
    for fl in os.listdir(modeldir):
        filepath = os.path.join(modeldir,fl)
        
        modelname = 'models.'
        
        for line in open(filepath).readlines():
#            print line+str(line.find('public'))
            
            if(line.find('class')>-1):
                table_name = line.split(" ")[2].lower()
                modelname = modelname + line.split(" ")[2]
                print modelname
#                print line.split(" ")[2]
#                print len(line.split(" ")[2])

#            if line.find('public')>-1 and line.find('class')==-1 and line.find('static')==-1:
#                print line.split(" ")[2][:-2]
#                print len(line.split(" ")[2][:-2])

        
        datasource = "select concat('select ',group_concat(concat('t.',column_name)),' from " + table_name + " t where 1=1') from information_schema.columns where table_schema='" + table_schema + "' and table_name='" + table_name + "' order by ordinal_position"
        cur.execute(datasource)
        selectsql = cur.fetchone()
        selectsql = ''.join(selectsql)
        print selectsql
        
        returnsql = "select group_concat(column_name) from information_schema.columns where table_schema='" + table_schema + "' and table_name='" + table_name + "' order by ordinal_position"
#        print datasource
        cur.execute(returnsql)
        returncolumn = cur.fetchone()
        returncolumn = ''.join(returncolumn)
        returncolumn = returncolumn + ',createby__display,' + ',updateby__display'
        print returncolumn
#        results = cur.fetchall()
#        for row in results:
#            returncolumn = row[0]
        notesql = "select name from menu where id=" + idnum
        cur.execute(notesql)
        notename = cur.fetchone()
        notename = ''.join(notename)
                
        sql = "insert into "+ table_schema +".meta_column value(" + idnum + ",'" + notename + "',1,'" + modelname + "','" + selectsql + "','',now(),now(),1,1,'','" + returncolumn + "','','','','')"
        cur.execute(sql)
        conn.commit()
        print sql
                
def menupermission(idmun):
    query = 'select id from menu where id=' + idnum
    cur.execute(query)
    results = cur.fetchall()
    for row in results:
        sql = "insert into menupermission value(" + str(row[0]) + ",1,0," + str(row[0]) + ",'',now(),1,now(),1)"
        cur.execute(sql)
        conn.commit()
        print sql
        
def metaform(idmun):
    query = 'select id,name from menu where id=' + idmun
    cur.execute(query)
    results = cur.fetchall()
    for row in results:
        sql = "insert into meta_form value(" + str(row[0]) + ",'" + str(row[0]) + "','" + str(row[1]) + "','" + str(row[1]) + "',1," + str(row[0]) + ",0,'','','',now(),now(),1,1,30)"
        cur.execute(sql)
        conn.commit()
        print sql

def metasubcolumn(idmun):
    
    select = "select id,substr(entityname,8) from meta_column where id=" + idmun
    cur.execute(select)
    results = cur.fetchall()
    
    idsql = 'select max(id) from meta_subcolumn where id<50000'
    cur.execute(idsql)
    idno = cur.fetchone()[0]
    
    idno = idno + 1
    
    for row in results:
        
        table_name = row[1].lower()
        
        query = "select concat('t!',column_name),column_comment from information_schema.columns where table_schema='" + table_schema + "' and table_name='" + table_name + "' order by ordinal_position"
        cur.execute(query)
        allcolume = cur.fetchall()
        
        for colume in allcolume:
            sql = "insert into meta_subcolumn value(" + str(idno) + "," + str(row[0]) + ",'" + colume[1] + "','" + colume[0] + "','" + colume[1] + "','left','',80,1,1,0,0,'','',1,6,1,'',0,0,0,1,'','','','',0,'',1,1,now(),now(),1,1,'',0,'',0,'')"
            idno = idno + 1
            cur.execute(sql)
            conn.commit()
            print sql
    
if __name__ == '__main__':
    
    dbconfigfile = 'D:\\db_local.conf'
    
    cf = ConfigParser.ConfigParser()
    cf.read(dbconfigfile)
    
    section = 'db_net'
    
    shost = cf.get(section, 'db1_host')
    sport = int(cf.get(section, 'db1_port'))
    suser = cf.get(section, 'db1_user')
    spd = cf.get(section, 'db1_pass')
    defaultdb = cf.get(section, 'db1_name')
    
    conn = MySQLdb.connect(host=shost, port=sport, user=suser, passwd=spd, db=defaultdb, charset='utf8')
    cur = conn.cursor()
    
    table_schema = defaultdb
    
    idnum = '4000013'
    
#    metacolumn(idnum)
#    menupermission(idnum)
#    metaform(idnum)
    metasubcolumn(idnum)