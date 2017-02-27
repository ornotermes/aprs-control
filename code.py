#!/usr/bin/env python2

#    Copyright 2017 Rikard Lindstrom SA5KPR <ornotermes@gmail.com>
#
#    This file is part of APRS-Control.
#
#    Foobar is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with APRS-Control.  If not, see <http://www.gnu.org/licenses/>.

import sys
import random
import sqlite3

from config import *

'''Print a table divider line'''
def tableSpacer():
    s = "+"
    for n in range(printColumns):
        s += "-" * ( 4 + len(str(codeCount)) + codeLength ) + "+"
    print s

conn = None
db = None
def dbQuery(sql):
    return db.execute(sql)

def dbOpen():
    '''Open database'''
    global conn, db
    conn = sqlite3.connect("codes.sqlite3")
    db = conn.cursor()
    '''Initialize database if needed'''
    db.execute("create table if not exists codes (call text, code text);")

def dbClose():
    '''Close database'''
    conn.commit()
    conn.close()

def generate(call):
    '''Generate new codes'''
    codes = []
    while len(codes) < codeCount:
        newCode = ""
        while ( len(newCode) < codeLength ):
            newChar = codeCharecters[random.randint(0,len(codeCharecters)-1)]
            if newCode == "":
                newCode = newChar
            if newCode[-1] != newChar:
                newCode += newChar
        if newCode not in codes:
            codes.append(newCode)
    
    '''Present new codes'''
    print("Codes for: {} on {}".format(call, myCall))
    tableSpacer()
    n = 0
    while (n < codeCount):
        s = "| "
        for m in range(0,printColumns):
            pos = n+m
            if pos in range(0, codeCount):
                s += str(pos+1).rjust(len(str(codeCount)),"0")
                s += ": "
                s += codes[pos] 
                s += " | "
            else:
                s += " " * ( 3 + len(str(codeCount)) + codeLength ) + "| "
        print (s)
        n+=printColumns
        tableSpacer()
    
    dbOpen()
    dbQuery("delete from codes where call='{}';".format(call))
    for code in codes:
        dbQuery("insert into codes (call, code) values('{}','{}');".format(call, code))
    dbClose()
    print ("New codes stored. Save your codes in a safe place.")

def revoke(call):
    '''remove credetials for callsign'''
    dbOpen()
    dbQuery("delete from codes where call='{}';".format(call))
    dbClose()
    print ("Revoked codes for {}".format(call))

def list():
    '''list callsigns and how many codes are left'''
    dbOpen()
    for row in dbQuery("select call, count(code) as codeCount from codes group by call"):
        print ("{} have {} code(s) left.".format(row[0],row[1]))
    dbClose()

def check(call, code):
    dbOpen()
    for row in dbQuery("select count(code) from codes where call='{}' and code='{}';".format(call.upper(), code.lower())):
        if row[0] > 0:
            print("Valid call and code , now revoked.")
            dbQuery("delete from codes where call='{}' and code='{}'".format(call.upper(), code.lower()))
        else:
            print("Invalid call and code!")
    dbClose()
    return row[0]

def admins():
    #list all admins
    dbOpen()
    return dbQuery("select call from codes group by call;")
    dbClose()

if __name__ == '__main__':
    error = True
    if len(sys.argv) > 1:
        operation = sys.argv[1].lower()
    if len(sys.argv) > 2:
        call = sys.argv[2].upper()
    if len(sys.argv) > 3:
        code = sys.argv[3].lower()
    if operation in ["check"]:
        check(call, code)
        error = False
    if operation in ["gen", "generate"]:
        generate(call)
        error = False
    if operation in ["rev", "revoke"]:
        revoke(call)
        error = False
    if operation in ["list"]:
        list()
        error = False
    if operation in ["?", "help", "-h", "--help"]:
        pass
    if error:
        print("Manage code database. Commands:")
        print("help|?          - This help")
        print("list            - List callsigns and how many codes they have")
        print("gen(erate) CALL - Generate new codes for CALL")
        print("rev(oke) CALL   - Revoke codes for CALL")
        print("check CALL CODE - Check validity and revoke if valid")
