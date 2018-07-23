# coding: utf-8
import os
import pymysql
import datetime,time
from ftplib import FTP
from PIL import Image
import random

imgtype = 3 #1三维人脸 2模糊图像 #3校准图像
dbip = "192.168.0.130"
dbbase = "u2am"
imagedirtype = "adjust" #third 三维 #blur模糊图像 #adjust校准图像
def getalldirectorys(path):
    allfile=[]
    for dirpath,dirnames,filenames in os.walk(path):
      for dir in dirnames:
          allfile.append(os.path.join(dirpath,dir))
      for name in filenames:
          continue
    return allfile

def all_directorys(path):
    allDirectorys = getalldirectorys(path)
    allChildDirectory = []
    for dirctory in allDirectorys:
        if is_child_directory(dirctory):
            allChildDirectory.append(dirctory)
    return allChildDirectory

def is_child_directory(dirctory):
    paths = os.listdir(dirctory)
    directorys = []
    for path2 in paths:
        if os.path.isdir(dirctory+os.sep+path2):
            directorys.append(path2)
    return len(directorys) == 0


def get_mysql_conn():
    #打开数据库连接
    db= pymysql.connect(host=dbip,user="root",password="Ast4HS",db=dbbase,port=3306)
    # 使用cursor()方法获取操作游标
    cur = db.cursor()
    return cur

def insert_third_people(cur,id):

    sql = "INSERT INTO third_people(id,create_time,status,c1) VALUES("+id+",'"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"',0,"+str(imgtype)+")"
    print sql
    try:
        cur.execute(sql) 	#执行sql语句
    except Exception as e:
        raise e

def insert_third_picture(cur,id,url,imgsize):
    sql = "INSERT INTO third_picture(people_id,pic_type,file_url,create_time,c1) VALUES("+id+",1,'"+url+"','"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"','"+imgsize+"')"
    try:
        cur.execute(sql) 	#执行sql语句
    except Exception as e:
        raise e


def syn_data(path):
    ftp = ftpconnect("192.168.0.130", "u2amftp", "123456")
    base_path = '/home/ftp/'+str(datetime.datetime.now().year)+'/'+str(datetime.datetime.now().month)+'/'+str(datetime.datetime.now().day)+'/face/'+imagedirtype+"/"
    #conn = get_mysql_conn()

    alldirectorys = all_directorys(path)
    for directory in alldirectorys:
        db= pymysql.connect(host=dbip,user="root",password="Ast4HS",db=dbbase,port=3306)
        # 使用cursor()方法获取操作游标
        conn = db.cursor()
        resourceid = get_random_num()
        remotepath = base_path+resourceid+'/'
        create_dir(ftp,remotepath)
        print directory
        insert_third_people(conn,resourceid)
        files = os.listdir(directory)
        for file in files:
            remote_file = remotepath+file
            local_file = directory+os.sep+file
            img = Image.open(local_file)
            imgsize = str(img.size[0])+"*"+str(img.size[1])
            insert_third_picture(conn,resourceid,remote_file,imgsize)
            file_handler = open(local_file, "rb")
            ftp.storbinary('STOR %s'%remote_file, file_handler, 4096)
            file_handler.close()
            #print remote_file
            #print local_file
        db.commit()
        conn.close()
    ftp.quit()
def ftpconnect(host, username, password):
    ftp = FTP()
    ftp.connect(host, 21)
    ftp.login(username, password)
    return ftp

def uploadfile(self,ftp, remotepath, localpath):
    bufsize = 1024
    fp = open(localpath, 'rb')
    ftp.storbinary('STOR ' + remotepath, fp, bufsize)
    ftp.set_debuglevel(0)
    fp.close()

def create_dir(ftp,dir_path):
        paths = str(dir_path).split('/')
        base_path = '/home/ftp'
        for path in paths:
            ftp.cwd(base_path)
            chirld = ftp.nlst()
            if ''!=path and 'home' != path and 'ftp' != path:
                base_path = base_path+'/'+path
                #print base_path
            if ''!=path and  'home' != path and 'ftp' != path and path not in chirld:
                ftp.mkd(base_path)

def get_random_num():
    nowTime=datetime.datetime.now().strftime("%Y%m%d%H%M%S");#生成当前时间
    randomNum=random.randint(0,100000);#生成的随机整数n，其中0<=n<=100
    if randomNum<=10:
        randomNum=str(0)+str(randomNum);
    uniqueNum=str(nowTime)+str(randomNum);
    return uniqueNum
if __name__ == '__main__':
  path = "D:/annotation/thirdfaceresult/result"
  syn_data(path)

  # imgpath = "D:/annotation/thirdfaceresult/result/Face2/obj_11/f_ns_4170.bmp"
  # img = Image.open(imgpath)
  # print str(img.size[0])+"*"+str(img.size[1])
  # print imgtype
  # print os.getcwd()
  #print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

