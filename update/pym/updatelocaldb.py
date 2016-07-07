#!/usr/bin/env python
#coding=utf-8
import os
import re

import MySQLdb
from Crypto.Cipher import AES

def decrypt(ciphertext):
    key = "" #根据自己的规则制定！
    mode = AES.MODE_CBC 
    IV = 16 * '\x00'
    
    decryptor = AES.new(key, mode,IV) 
    ciphertext = ciphertext[1:len(ciphertext)]
    ciphertext = ciphertext.decode('hex');
    plain = decryptor.decrypt(ciphertext)
    padlen = ord(plain[len(plain)-1])
    return plain[0:len(plain)-padlen]

#acquire each sql list file from a path ,separated  in a different list  by execute database type
def acquiresqlfile(path):
    wtlist = []
    TSfile = []
    TIfile = []
    TVfile = []
    PDfile = []
    DTfile = []
    for item in os.listdir(path):
        subpath = os.path.join(path, item)
        isfile = os.path.isfile(subpath)
        if isfile:
            if re.search('_TS_', subpath):
                TSfile.append(subpath)
            elif re.search('_TI_', subpath):
                TIfile.append(subpath)
            elif re.search('_TV_', subpath):
                TVfile.append(subpath)
            elif re.search('_PD_', subpath):
                PDfile.append(subpath)
            elif re.search('_DT_', subpath):
                DTfile.append(subpath)
            # else:
            #     print("%S is not a norm sql file") % uwtdatafile
            # uwtlist.append(uwtdatafile)
    wtlist.append(TSfile)
    wtlist.append(TIfile)
    wtlist.append(TVfile)
    wtlist.append(PDfile)
    wtlist.append(DTfile)
    return wtlist


#generate split sql use ';' or With @begin  @end
def splitsql(alllist):

    # sqlsetlist = []
    s = ""
    sqlset = []
    for sqlfilelist in alllist:
        s = ""
        for sqlfile in sqlfilelist:
            s = ""
            if sqlfile.__len__() > 0:
                ##sqlfile="D:\\Python27\\SQL\\1.4\\wt\\bus_TS_WT_V140.sql"
                print(sqlfile)
                f = open(sqlfile)
                bcheckbegin=0
                for line in f:
                    matchAuth = re.search('##', line)
                    matchrep = re.search('@repeat', line)
                    matchnorep = re.search('@norepeat', line)
                    matchb = re.search('--beginblock', line)
                    matche = re.search('--endblock', line)
                    matchend = re.search(';', line)
                    if matchb:
                        bcheckbegin = 1
                    elif matchAuth:
                        s = s
                    elif matchrep:
                        s = s + line
                    elif matchnorep:
                        s = s + line
                    elif matchend:
                        if bcheckbegin == 0:
                            s = s + line[:matchend.end()]
                            sqlset.append(s)
                            s = ""
                        else:
                            s = s + line
                    elif matche:
                        sqlset.append(s)
                        s = ""
                        bcheckbegin = 0
                    else:
                        s = s + line

    return sqlset

g_sqlcount=0    #所以脚本数量
g_errorcount=0  #执行错误脚本数量
g_norepeatcount=0   #不能重复执行梳理
g_repeatcheckexeccount=0    #有重复检查SQL的脚本梳理
g_sqlignorecount=0          #忽略掉的脚本数量

def executeNSQL(sql, cur):
    global g_sqlcount    #所以脚本数量
    global g_errorcount  #执行错误脚本数量
    global g_norepeatcount   #不能重复执行梳理
    global g_repeatcheckexeccount    #有重复检查SQL的脚本梳理
    global g_sqlignorecount          #忽略掉的脚本数量
    matchre = re.search('@repeat', sql)
    matchnore = re.search('norepeat', sql)
    matchleft = re.search('{', sql)
    matchright = re.search('}', sql)
    berror=0
    checkSql = ""
    s = ""
    okChkSql = 1
    noreport=0
    if matchre:
        noreport=2
        if matchleft:
            if matchright:
                checkSql = sql[matchleft.end():matchright.start()]
                s = sql[matchright.end():]
                if len(checkSql) == 0:
                    okChkSql = 0
        else:
            okChkSql=0
            s = sql[matchre.end():]
    elif matchnore:
        s = sql[matchnore.end():]
        noreport=1
        okChkSql = 0
    else:
        s = sql
        okChkSql = 0
        checkSql = ""

    try:
        if len(checkSql) > 0:
            checkSqlt=checkSql.replace('@@dbname','buspre')
            cur.execute(checkSqlt)
            okcChSqllist = cur.fetchone()
            okChkSql = okcChSqllist[0]
            g_repeatcheckexeccount=g_repeatcheckexeccount+1
    except MySQLdb.Error as e:
        print("[check error] %s") % checkSql

    
    try:
        if len(s)>0:
            g_sqlcount=g_sqlcount+1
            if okChkSql == 0:
                cur.execute(s)
                #print('[success exec] %s') % s
            else:
                g_sqlignorecount=g_sqlignorecount+1
                #print('[cannot exec] %s') % s
            #if noreport==0:
                #print('[noauth] %s') % s
            if noreport==1:
                g_norepeatcount=g_norepeatcount+1
                #print('[noreport] %s') % s

    except MySQLdb.Error as e:
        print("[error] %s") % e
        print("[sql] %s") % s
        g_errorcount=g_errorcount+1
        berror=1
    return berror
    


def executeSingleDB(sqlsetlist, cursor, conn):
    isAllExecute = 1
    if sqlsetlist.__len__() > 0:
        try:
            for usql in sqlsetlist:
                executeNSQL(usql, cursor)
                
        except MySQLdb.Error as e:
            print("Mysql Error %d: %s") % (e.args[0], e.args[1])
            isAllExecute = 0
    if isAllExecute == 1:
        conn.commit()
    elif isAllExecute == 0:
        conn.rollback()

#    cursor.close()
#    conn.close()

def getProperties(filename):
    p = open(filename)
    properties = {}
    for line in p.readlines():
        if not line:
            continue
        if line.strip().startswith("#"):
            continue
        if line.find('=') > 0:
            strs = line.strip().split('=')
            properties[strs[0].strip().lower()] = strs[1].strip()
    p.close()
    return properties

def execsql(cfgname,dbdir,patchdir):
    ps = getProperties(cfgname)
    shost = '';
    sport = '';
    sdb = '';
    suser = '';
    spasswd = '';
    for (k, v) in ps.items():
        if 'db_local.url' == k :
            shost = v.split(':')[2][2:]
            sport = v.split(shost)[1].split('/')[0][1:]
            sdb = v.split(shost)[1].split('/')[1].split('?')[0]
        if 'db_local.user' == k :
            suser = v
        if 'db_local.pass' == k :
            if v.startswith('^'):
                spasswd = decrypt(v)
            else:
                spasswd = v
    conn = MySQLdb.connect(host=shost, port=int(sport), db=sdb, user=suser, passwd=spasswd, charset='utf8')
    cursor = conn.cursor();
    
    sqlfilelist = acquiresqlfile(dbdir)
    sqlsetlist = splitsql(sqlfilelist)
    executeSingleDB(sqlsetlist, cursor, conn)
    
    sqlfilelist = acquiresqlfile(patchdir)
    sqlsetlist = splitsql(sqlfilelist)
    executeSingleDB(sqlsetlist, cursor, conn)
    
#    strs = ("所有脚本数量=%d") % g_sqlcount
#    strs += ("执行错误脚本数量=%d") % g_errorcount
#    strs += ("不能重复执行的脚本语句数量=%d") % g_norepeatcount
#    strs += ("有重复检查脚本的SQL语句数量=%d") % g_repeatcheckexeccount
#    strs += ("忽略掉的脚本语句数量=%d") % g_sqlignorecount
#    sql = "insert into updatelog(project,isok,message) values ('%s', %d,'%s')" % ("BusSale", 0,strs)
#    try:
#        print sql
#        cursor.execute(sql)
#        conn.commit
#    except Exception, e:
#        print e
    
    cursor.close()
    conn.close()
    
    print("--------------------------执行结果------------------------")
    print("所有脚本数量=%d") % g_sqlcount
    print("执行错误脚本数量=%d") % g_errorcount
    print("不能重复执行的脚本语句数量=%d") % g_norepeatcount
    print("有重复检查脚本的SQL语句数量=%d") % g_repeatcheckexeccount
    print("忽略掉的脚本语句数量=%d") % g_sqlignorecount
    print("--------------------------执行完毕------------------------")
