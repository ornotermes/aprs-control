#!/usr/bin/env python2

import aprslib
import logging
import socket
import sqlite3
import time
import os

from config import *
import code

logging.basicConfig(level=logging.DEBUG) # level=10

ais = None

def validAdmin(package):
    call = package['from']
    c = package['message_text'][-codeLength:]
    ret = code.check(call, c)
    print ("Auth: {} / {} is {}.".format(call, c, "valid" if ret else "invalid" ))
    if ret == False:
        send(myCall, package['from'], "Invalid auth")
    return ret

def send(sender,reciever,message):
    pkg = sender + ">APRS,TCPIP*::" + reciever.ljust(9,' ') + ":" + message
    print("Sending> "+pkg)
    ais.sendall(pkg)

def interpret(package):
    if 'addresse' in package:
        if package['addresse'] == myCall:
            print package
            time.sleep(2) #Give the radio som time to get ready to recieve
            msg = package['message_text'].lower()
            #return OK
            if msg in ["stat", "status"]:
                send(myCall, package['from'],u"OK");
            #return LAN IP
            if msg == "ip":
                send(myCall, package['from'],\
                    "LAN:"+[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1])
            #reboot system, require admin
            if msg[:6] == "reboot" and validAdmin(package):
                send(myCall, package['from'],"Rebooting...");
                print( "Rebooting..." );
                os.system("sudo reboot")
            #shutdown system, require admin
            if msg[:8] == "shutdown" and validAdmin(package):
                send(myCall, package['from'], "Shuting down...")
                print("Shuting down...")
                os.system("sudo poweroff")
def process(package):
    if myCall in package:
        try:
            interpret(aprslib.parse(package))
        except (aprslib.ParseError, aprslib.UnknownFormat) as exp:
            pass

def anounce():
    for admin in code.admins():
        send( myCall, admin[0], "is online!")

def connect():
    global ais
    ais = aprslib.IS(myCall,myPass)
    ais.connect(blocking=True)
    anounce()
    ais.consumer(process, raw=True)

try:
    connect()
except (aprslib.ConnectionDrop, aprslib.ConnectionError) as e:
    print ("Connection error!\n" + e)
    time.sleep(3)
    connect()
