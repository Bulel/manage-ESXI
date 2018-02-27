#-*- encoding: utf-8 -*-
# @function: shutdown esxi after if one host of ESXI is down
# @author:   bulel

import paramiko
import time
import os
import sys

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())               #ignore ssh key verify


client.connect('192.168.1.98', username='root', password='arrayclick1')    # address of esxi

stdin, stdout, stderr = client.exec_command('uname')

print("-"*60)
for line in stdout:

    print('... ' + line.strip('\n'))
    
    if line.strip('\n') == "VMkernel":
        print("Login ESXI successfully\r\n")

print("-"*60)

while True:
    resp = os.popen("ping -n 4 192.168.1.121").read()                      # one host of ESXI
    
    print("Result of detect: \r\n"+"-"*60,resp)
    print("-"*60)
    
    if  "无法访问" in resp:
        print("Host is down,will shutdown ESXI after 60 s;")
        
        for i in range(1,61)[::-1]:
            time.sleep(1)                                                 # display process, cover old dispaly
            sys.stdout.write(' ' * 10 + '\r')
            sys.stdout.flush()
            sys.stdout.write('%d s\r'%i)
            sys.stdout.flush()
            print("%d"%i,end="\r")
        client.exec_command('poweroff')   #init 0 may also can shutdown ESXI
        client.close()
        print("-"*60)
    else:
        print("Host is up")
        print("-"*60)    
        time.sleep(1800)       #if host is up, sleep 30 minutes, then detect again
