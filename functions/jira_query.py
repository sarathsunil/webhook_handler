import os
import sys
import json
import requests
import random
import string
def jira_query_pull(issues_url,session_cookie):
    headers = {
           'connection': "keep-alive",
           'upgrade-insecure-requests': "1",
           'cache-control': "no-cache",
           'content-type': 'application/json',
           'cookie': 'JSESSIONID='+session_cookie
           }
    response = requests.get(issues_url, headers=headers, verify=False).json()
    project_id = str(response['fields']['project']['id'])
    title = response['fields']['summary']
    description = response['fields'][customer_description_id]
    release_tag = response['fields'][release_tag_id]
    return {"project_id":project_id,"title":title,"description":description,"release_tag":release_tag}

def jira_validate(issue_url,session_cookie):
    headers = {
           'connection': "keep-alive",
           'upgrade-insecure-requests': "1",
           'cache-control': "no-cache",
           'content-type': 'application/json',
           'cookie': 'JSESSIONID='+session_cookie
           }
    response = requests.get(issue_url, headers=headers, verify=False).json()
    status = str(response['fields']['status'])
    return status
    
def jira_query_update(username,password,field_id,ip,port,issue_id):
    # headers = {
    #         'connection': "keep-alive",
    #         'upgrade-insecure-requests': "1",
    #         'cache-control': "no-cache",
    #         'content-type': 'application/json',
    #         'cookie': 'JSESSIONID='+session_cookie
    #         }
    # data = json.dumps({"fields":{field_id:[{"value":"Yes"}]}})
    # response = requests.request('PUT', issues_url, data=data, headers=headers,verify=False)
    # return response.status_code
    curl_string = r"""curl -D- -u 'myusername:mypassword' -X PUT --data "{\"fields\":{\"my_field_id\":{\"value\" : \"Yes\"}}}" -H "Content-Type: application/json" http://my_jira_ip:my_jira_port/rest/api/latest/issue/my_issue_id/"""
    curl_string = curl_string.replace('myusername',username)
    curl_string = curl_string.replace('mypassword',password)
    curl_string = curl_string.replace('my_field_id',field_id)
    curl_string = curl_string.replace('my_jira_ip',ip)
    curl_string = curl_string.replace('my_jira_port',str(port))
    curl_string = curl_string.replace('my_issue_id',issue_id)
    os.system('sudo '+curl_string+' >/home/curl_out')
    try:
       return open('/home/curl_out','r').read().split('\n').split()[1]
    except IndexError:
       return 404
    #filename_out = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
    #os.system("cat /tmp/curl_writer | /bin/bash > /tmp/"+filename_out)
    #return open('/tmp/'+filename_out,'r').read().split('\n')[0].split()[1]
