# coding: utf-8
import os
import pymysql
import datetime,time,json,threading
from ftplib import FTP
from PIL import Image
import random,requests
import httplib, urllib


imgtype = 2 #1三维人脸 2模糊图像 #3校准图像
picture_base = 'http://192.168.0.130:8088/'
db_name = "u2am_test"
def get_angle_by_url(imageurl):
    #r = requests.post("http://192.168.0.130:3456/facepose?imageName="+str(imageurl))
    text =  requests.get("http://192.168.0.130:3456/facepose?imageName="+str(imageurl)).text
    result = json.loads(text)
    if result['successFlag'] == '1':
        return result['angle']
    else:
        return '0'

#http://192.168.0.130:8088/ftp/2018/7/13/face/201807131528457297/f_ss_792.bmp
def syn_angle():
    db= pymysql.connect(host="192.168.0.130",user="root",password="Ast4HS",db=db_name,port=3306)
    cursor = db.cursor()
    cursor.execute("SELECT id from third_people WHERE c1="+str(imgtype))
    persons = cursor.fetchall()
    for person in persons:
        picturessql = "select id,file_url from third_picture WHERE people_id="+str(person[0])
        cursor.execute(picturessql)
        pictures = cursor.fetchall()

        db2= pymysql.connect(host="192.168.0.130",user="root",password="Ast4HS",db=db_name,port=3306)
        conn = db2.cursor()
        for picture in pictures:
            pictureid = picture[0]
            pictureurl = picture[1]
            imageurl = picture_base+pictureurl[6:]
            print imageurl
            angle =  get_angle_by_url(imageurl)
            print angle
            sql = "update third_picture set angle ='"+str(angle)+"' where id="+str(pictureid)
            print sql
            try:
                conn.execute(sql) 	#执行sql语句
            except Exception as e:
                raise e
        db2.commit()
        conn.close()
    # 关闭数据库连接
    db.close()
if __name__ == '__main__':
    syn_angle()
   # print get_angle_by_url('123')