# coding: utf-8
import requests
from bs4 import  BeautifulSoup
baseurl = "http://xuexiao.51sxue.com/slist/"
#
lx = [u'幼儿园',u'小学',u'中学',u'职业学校',u'培训机构',u'大学']
sxyey = [u'师范幼儿园',u'一级幼儿园',u'二级幼儿园',u'三级幼儿园',u'其他']
sxxx = [u'全国重点',u'省重点',u'市重点',u'县重点',u'区重点',u'普通']  #小学中学职业中学
xz = [u'公办',u'民办',u'私立']
for i,kind in enumerate(lx):
    for j,sx in enumerate(sxxx):
        for k,sz in enumerate(xz):
            url=baseurl+"?o=&t="+str((i+1))+"&areaCodeS=4301&level="+str((j+1))+"&sp="+str((k+1))+"&score=&order=&areaS=%B3%A4%C9%B3%CA%D0&searchKey="
            print(url)
            response = requests.get(url)
            response.encoding='gbk'
            content = response.text
            mainsoup = BeautifulSoup(content)
            result = mainsoup.find(class_='school_main')
            print(result)
            if '没有相关记录' in str(result):
                print(111)
            else:
                print(222)
