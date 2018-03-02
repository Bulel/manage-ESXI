#-*- encoding: utf-8 -*-
# @function: shutdown esxi after one host is down
# @author:   bulel

import paramiko
import time
import os
import sys


def mlog(log):       
        m=open('esxilog.txt','a')
        date=time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
        date=str(date)
        msg=date+" - "+log
        m.write(msg+"\n\n")
        m.close()


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


try:
    client.connect('192.168.1.99', username='root', password='arrayclick1')

    stdin, stdout, stderr = client.exec_command('uname')

    print("-"*60)
    for line in stdout:

        print('... ' + line.strip('\n'))
    
        if line.strip('\n') == "VMkernel":
            print("Login ESXI successfully\r\n")
            mlog("Login ESXI successfully")

    print("-"*60)

except:
        fail = "Fail to login"
        print(fail)
        mlog(fail)

while True:
    resp = os.popen("ping -n 4 192.168.1.91").read()
    
    print("Result of detect: \r\n"+"-"*60,resp)
    print("-"*60)
    
    if  "无法访问" in resp:
        down = "Host is down,will shutdown ESXI after 60 s;"
        print(down)
        mlog(down)
        
        for i in range(1,61)[::-1]:
            time.sleep(1)
            sys.stdout.write(' ' * 10 + '\r')
            sys.stdout.flush()
            sys.stdout.write('%d s\r'%i)
            sys.stdout.flush()
            print("%d"%i,end="\r")
        client.exec_command('poweroff')   #init 0 may also can shutdown ESXI
        mlog("poweroffed")
        client.close()
        print("-"*60)
    else:
        up = "Host is up"
        print(up)
        mlog(up)
        print("-"*60)    
        time.sleep(1800)       #if host is up, sleep 30 minutes, then detect again
