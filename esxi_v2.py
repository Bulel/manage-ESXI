#-*- encoding: utf-8 -*-
# @function: shutdown esxi after smoketest is finished
# @author:   bulele

import win32security
import win32api
import win32con
import paramiko
import time
import os
import sys
import re

#### get the shutdown privilege

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



def detect_status():
    stdin, stdout, stderr = client.exec_command('vim-cmd vmsvc/getallvms')

    vm=[]

    print("+"*60 + "\r\n")
    mlog("Will detect all up hosts and power off them")
    print("\r\n")
    for line in stdout:

        #get all the vms, because esxi print some other info of kali, so need to separate
        if re.search(r'(.+?datastore)',line):

              
            raw = re.search(r'(.+?datastore)',line)
            reg = raw.group(1)

            spi = reg.split()
            vm.append(spi[0])
        
            #print("Vmid " + str(spi[0]) + ": " + str(spi[1]) + "\r\n") #spi[0:2]


            stdin, stdout, stderr = client.exec_command('vim-cmd vmsvc/power.getstate ' + spi[0])

            s_0 = ''
            for ss in stdout:
                s_0 = s_0 + ss

            #get all the up host
            if re.search(r'(Powered on)',s_0):

                print("-"*60)
                raw_status = re.search(r'(Powered on)',s_0)
                mlog("The up host: " + spi[1])
                
                ######## here will shutdown up host
                mlog("will power off " + spi[1])
                stdin, stdout, stderr = client.exec_command('vim-cmd vmsvc/power.off ' + spi[0])
                time.sleep(6)

                while 1:

                     stdin, aaa, stderr = client.exec_command('vim-cmd vmsvc/power.getstate ' + spi[0])
                     status = ''
                     
                     for s in aaa:

                         status = status + s

                     if re.search(r'(Powered on)',s):
                         mlog("Not power off, will power off again " + spi[1])
                         
                         # Did not change stdout to bbb, failed to execute the cmd, so change it, do not know why
                         stdin, bbb, stderr = client.exec_command('vim-cmd vmsvc/power.off ' + spi[0])  
                         time.sleep(6)
                         continue
                     else:
                         mlog("powered off " + spi[1])
                         break
                             
            else:
                pass
 
        else:
            pass

    print("-"*60 + "\r\n")
    print("+"*60)



try:
    client.connect(esxi_host, username='root', password='arrayclick1')

    stdin, stdout, stderr = client.exec_command('uname')

    print("-"*60)
    for line in stdout:

        print('... ' + line.strip('\n'))

        if line.strip('\n') == "VMkernel":
            
            mlog("Login ESXI %s successfully"%esxi_host)

    print("-"*60 + "\r\n")

except:
        mlog("Fail to login")



while True:
    resp = os.popen("ping -n 4 " + vm_host).read()
    
    print("Result of detect: \r\n"+"-"*60,resp)
    print("-"*60)
    
    if  "无法访问" in resp:

        down = "Host %s is down, will detect up host and shutdown ESXI %s after off all hosts in 10 s;"%(vm_host,esxi_host)
        mlog(down)
        detect_status()
        
        for i in range(1,10)[::-1]:
            time.sleep(1)
            sys.stdout.write(' ' * 10 + '\r')
            sys.stdout.flush()
            sys.stdout.write('%d s\r'%i)
            sys.stdout.flush()
            print("%d"%i,end="\r")

        client.exec_command('poweroff')   #init 0 may also can shutdown ESXI
        mlog("poweroffed ESXI %s"%esxi_host)
        client.close()
        print("-"*60)

        time.sleep(3)

        msg = 'Will shutdown the PC after 10 seconds'       
        #win32api.InitiateSystemShutdown(None,msg,10,1,0) #InitiateSystemShutdown(computerName, message, timeOut, bForceClose, bRebootAfterShutdown)
        mlog(msg)
        
        break

    else:
        up = "Host %s is up"%vm_host
        mlog(up)
        print("-"*60)    
        time.sleep(d_time)       #if host is up, sleep d_time seconds, then detect again
