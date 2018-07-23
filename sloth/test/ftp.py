# coding: utf-8
from ftplib import FTP
import ftplib
import time
import tarfile
import os,json,datetime,time,sys
# !/usr/bin/python
# -*- coding: utf-8 -*-

from ftplib import FTP

def ftpconnect(host, username, password):
    ftp = FTP()
    # ftp.set_debuglevel(2)
    ftp.connect(host, 21)
    ftp.login(username, password)
    return ftp

#从ftp下载文件
def downloadfile(ftp, remotepath, localpath):
    bufsize = 1024
    fp = open(localpath, 'wb')
    ftp.retrbinary('RETR ' + remotepath, fp.write, bufsize)
    ftp.set_debuglevel(0)
    fp.close()

#从本地上传文件到ftp
def uploadfile(ftp, remotepath, localpath):
    bufsize = 1024
    fp = open(localpath, 'rb')
    ftp.storbinary('STOR ' + remotepath, fp, bufsize)
    ftp.set_debuglevel(0)
    fp.close()

def uploadPic(jsonpath,taskid):
    f = open(jsonpath)
    strJson = json.load(f)
    timeseconds = str(time.time())
    print timeseconds
    ftp = ftpconnect("192.168.0.130", "u2amftp", "123456")
    remotepath = '/home/ftp/'+str(datetime.datetime.now().year)+'/'+str(datetime.datetime.now().month)+'/'+str(datetime.datetime.now().day)+'/'+taskid+'/'+timeseconds[:timeseconds.find(".")]+'/'
    create_dir(ftp,remotepath)
    labels = strJson['labels']
    local_base_path = jsonpath[:jsonpath.rfind('/')+1]
    for label in labels:
        file_remote_path = remotepath+label['filename']
        uploadfile(ftp, file_remote_path, local_base_path+label['filename'])
    ftp.quit()

def create_dir(ftp,dir_path):
    paths = str(dir_path).split('/')
    base_path = '/home/ftp'
    for path in paths:
        ftp.cwd(base_path)
        chirld = ftp.nlst()
        if ''!=path and 'home' != path and 'ftp' != path:
            base_path = base_path+'/'+path
            print base_path
        if ''!=path and  'home' != path and 'ftp' != path and path not in chirld:
            ftp.mkd(base_path)
if __name__ == "__main__":
    #jsonstr = 'D:/annotation/hisense1/hisense1_vehiclepart/hisense1_vehiclepart0.json'
    #uploadPic(jsonstr,'123456')
    str = 'GLST                                                                                      &1525681829746'
    print str.split('&')[1]