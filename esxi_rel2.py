#-*- encoding: utf-8 -*-
# @function: shutdown esxi after one vm is down
# @author:   bulel

import win32security
import win32api
import win32con
import paramiko
import time
import os
import sys

#### get the shutdown privilege, (shutdown local pc)

p1 = win32security.LookupPrivilegeValue(None, win32con.SE_SHUTDOWN_NAME)
htoken = win32security.OpenProcessToken(win32api.GetCurrentProcess(),win32con.TOKEN_ALL_ACCESS)

newstate = [(p1, win32con.SE_PRIVILEGE_ENABLED)]

# Grab the token and adjust its privileges.
win32security.AdjustTokenPrivileges(htoken, False, newstate)

####


print("="*36)
esxi_host = input("Please input ip of ESXI: \r\n")
print("="*36)
vm_host = input("Please input ip of vm: \r\n")
print("="*36)
d_time = int(input("Please input interval of detecting: \r\n"))
print("="*36+"\r\n")

def mlog(log):       
        m=open('esxilog.txt','a')
        print(log+"\r\n")
        date=time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time()))
        date=str(date)
        msg=date+" - "+log
        m.write(msg+"\n\n")
        m.close()


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


try:
    client.connect(esxi_host, username='root', password='arrayclick1')

    stdin, stdout, stderr = client.exec_command('uname')

    print("-"*60)
    for line in stdout:

        print('... ' + line.strip('\n'))
    
        if line.strip('\n') == "VMkernel":
            mlog("Login ESXI %s successfully"%esxi_host)

    print("-"*60)

except:
        mlog("Fail to login")

while True:
    resp = os.popen("ping -n 4 " + vm_host).read()
    
    print("Result of detect: \r\n"+"-"*60,resp)
    print("-"*60)
    
    if  "无法访问" in resp:
        down = "Host %s is down,will shutdown ESXI %s after 10 s;"%(vm_host,esxi_host)
        mlog(down)
        
        for i in range(1,10)[::-1]:
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
        
        time.sleep(3)

        msg = 'Will shutdown the PC after 10 seconds'       
        win32api.InitiateSystemShutdown(None,msg,10,1,1) 
        #InitiateSystemShutdown(computerName, message, timeOut, bForceClose, bRebootAfterShutdown)
        mlog(msg)
        
        break
        
    else:
        up = "Host %s is up"%vm_host
        mlog(up)
        print("-"*60)    
        time.sleep(d_time)       #if host is up, sleep d_time seconds, then detect again
