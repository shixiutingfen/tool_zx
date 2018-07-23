# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

#!/usr/bin/python
import urllib2,json
def get_task():
    request_dict = {"app_id":"suntek"}
    request_data = json.dumps(request_dict).encode("utf-8")
    request = urllib2.Request(url = "http://192.168.0.145:8080/u2am/rest/webService/queryAllTask",
    headers = {'Content-Type' : 'application/json','charset':'UTF-8'},
    data = request_data)
    response = urllib2.urlopen(request)
    result = response.read()
    return result

def get_task_list():
    json_str = get_task()
    hjson = json.loads(json_str)
    result_list = []
    for task in hjson['tasks']:
        task_id_name = task['name']+'                                                                                      &'+str(task['id'])
        result_list.append(task_id_name)
    return result_list

def add_resource(taskid,resourceid,jsonPath):
    # request_dict = {"taskId":str(taskid),"resourceId":str(resourceid),"filePath":str(jsonPath)}
    # request_data = json.dumps(request_dict).encode("utf-8")
    url = 'http://192.168.0.145:8080/u2am/rest/webService/addTaskFile?taskId='+str(taskid)+'&resourceId='+str(resourceid)+'&filePath='+str(jsonPath)
    request = urllib2.Request(url = url,
    headers = {'Content-Type' : 'application/json','charset':'UTF-8'})
    response = urllib2.urlopen(request)
    result = response.read()
    return result

if __name__ == '__main__':
    print get_task_list()