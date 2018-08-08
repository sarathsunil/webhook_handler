#!usr/bin/python
import json
import jinja2
import os
from flask import Flask, jsonify, render_template
from flask import abort
from flask import make_response
from flask import request, Response
import logging
import glob
import requests
from settings.credentials import JIRA_USERNAME as JIRA_USERNAME,JIRA_PASSWORD as JIRA_PASSWORD
from settings.urls_all import JIRA as JIRA_IP
from settings.ports_all import JIRA as JIRA_PORT
from settings.jira_fields import customer_description as CUSTOMER_DESCRIPTION
from settings.jira_fields import release_tag as RELEASE_TAG
from settings.jira_fields import code_integration as CODE_INTEGRATION
from functions.authorization import get_session_cookie
from functions.html_renderer import html_parse
from functions.jira_query import jira_query_pull,jira_validate,jira_query_update,jira_field_id_mapping,jira_release_tag_look_up
from functions.none_checker import check_for_none
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
application = Flask(__name__)


def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))
#@application.route('/commits/api/v1.0/releasenotes/<project_id>', methods=['GET'])
#def html_render(project_id,customer_description,project_name,release_tag,issue_id):
#        writer = open(root_dir()+'/data/releasenote_'+project_name+'_'+issue_id+'_'+release_tag+'.html','w')
#        writer.write(render_template('template.html', project_id=project_id, customer_description=customer_description,project_name=project_name))
#        writer.close()
#        return render_template('template.html', project_id=project_id, customer_description=customer_description,project_name=project_name)

def get_latest_releasenotes():  # pragma: no cover
    try:
        # list all the files in the directory
        directory = root_dir()+'/data/'
        files = os.listdir(root_dir()+'/data/')
        # remove all file names that don't match partial_file_name string
        #files = filter(lambda x: x.find(partial_file_name) > -1, files)
        # create a dict that contains list of files and their modification timestamps
        name_n_timestamp = dict([(x, os.stat(directory+x).st_mtime) for x in files])
        # return the file with the latest timestamp
        newest= max(name_n_timestamp, key=lambda k: name_n_timestamp.get(k))
        return open(root_dir()+'/data/'+newest,'r').read()
    except IOError as exc:
        #logger.error("Redirection error")
        return str(exc)
@application.route('/')
def home():
    return render_template('home.html')
@application.route('/regenerate')
def regenerate():
    return render_template('generate.html')
@application.route('/commits/api/v1.0/releasenotes/latest/', methods=['GET'])
def metrics():  # pragma: no cover
    content = get_latest_releasenotes()
    return Response(content, mimetype="text/html")
@application.route('/todo/api/v1.0/releasenotes/generate/', methods=['POST'])
def get_tasks():
    #writer = open('cache-writer.txt','w')
    #writer.write(tasks)
    #print request.headers
    data = {}
    if request.headers['Content-Type'] == 'application/json':    
        print request.data
        data = json.loads(request.data)
    else:
        return make_response(jsonify({'error':'Content-type is unsupported'}),400)
    if 'commit_message' in data.keys():
        logger.info("COMMIT MESSAGE:"+"\n"+data['commit_message'])
        ISSUE_ID = data['commit_message'].split(":")[0]
        JIRA_AUTHORIZATION_URL = "http://"+JIRA_IP+":"+str(JIRA_PORT)+"/rest/auth/1/session/"
        JIRA_ISSUES_URL = "http://"+JIRA_IP+":"+str(JIRA_PORT)+"/rest/api/latest/issue/"+ISSUE_ID+"?expand=names"
        JIRA_ISSUES_URL_BASE = "http://"+JIRA_IP+":"+str(JIRA_PORT)+"/rest/api/2/issue/"+ISSUE_ID+"/"
        jsessionid = get_session_cookie(JIRA_USERNAME,JIRA_PASSWORD,JIRA_AUTHORIZATION_URL)
        logger.info("SESSION COOKIE :"+str(jsessionid))
        if jsessionid["values"] != False:
            jsessionid = jsessionid["JSESSIONID"]
            HEADERS = {
             'connection': "keep-alive",
             'upgrade-insecure-requests': "1",
             'cache-control': "no-cache",
             'content-type': 'application/json',
             'cookie': 'JSESSIONID='+jsessionid
            }

            wi_status = jira_validate(JIRA_ISSUES_URL,jsessionid)
            logger.info("WI STATUS : "+wi_status)
            if wi_status == 'Done' or wi_status == 'done':
               return jsonify({'errorMessages':["Work item is already in done state, please revise work item Id in the commit message"]})
            response = requests.get(JIRA_ISSUES_URL, headers=HEADERS, verify=False).json()
            customer_description_id = jira_field_id_mapping(CUSTOMER_DESCRIPTION,ISSUE_ID,JIRA_IP,JIRA_PORT,jsessionid)
            logger.info("CUSTOMER DESC ID : "+str(customer_description_id))
            release_tag_id = jira_field_id_mapping(RELEASE_TAG,ISSUE_ID,JIRA_IP,JIRA_PORT,jsessionid)
            logger.info("RELEASE TAG ID : "+str(release_tag_id))
            code_integration_id = jira_field_id_mapping(CODE_INTEGRATION,ISSUE_ID,JIRA_IP,JIRA_PORT,jsessionid)
            if(jira_query_update(JIRA_USERNAME,JIRA_PASSWORD,code_integration_id,JIRA_IP,JIRA_PORT,ISSUE_ID)!='204'):
                logger.info("COULD NOT UPDATE WORK ITEM CODE INTEGRATION ID--CODE RECEIVED : "+str(jira_query_update(JIRA_USERNAME,JIRA_PASSWORD,code_integration_id,JIRA_IP,JIRA_PORT,ISSUE_ID)))
            logger.info("CODE INT ID : "+str(code_integration_id))
            project_id = check_for_none(response['fields']['project']['id'])
            logger.info("PROJECT ID : "+str(project_id))
            jira_project_name = check_for_none(response['fields']['project']['name'])
            logger.info("PROJECT NAME : "+str(jira_project_name))
            release_tag = check_for_none(response['fields'][release_tag_id])
            logger.info("RELEASE TAG : "+str(release_tag))
            #jira_query_update(JIRA_USERNAME,JIRA_PASSWORD,code_integration_id,JIRA_IP,JIRA_PORT,ISSUE_ID)
            description = jira_release_tag_look_up(JIRA_IP,JIRA_PORT,jsessionid,jira_project_name,release_tag,customer_description_id)
            logger.info("DESCRIPTION : "+"\n"+description)
            title = check_for_none(response['fields']['summary'])
            issue_id = ISSUE_ID
            release_note_name = "Release-Notes-"+jira_project_name+"-"+release_tag+".html"
            html_parse(root_dir()+'/templates/template.html',root_dir()+'/data/'+release_note_name,project_id,issue_id,description,jira_project_name,release_tag)
            return make_response(jsonify({'success':'release notes generated for Release Tag:'+release_tag}), 200)
        else:
            return make_response(jsonify({'error':'JIRA Login failed'}), 403)
    else:
        return make_response(jsonify({'error':'parameter commit_message is missing from request body'}),400)

@application.route('/commits/api/v1.0/releasenotes/')
def release_lookup():
    logger.info("PROJECT NAME FOR LOOKUP : "+request.args.get('project_name'))
    logger.info("RELEASE TAG ID FOR LOOKUP : "+request.args.get('release_tag'))
    logger.info("RELEASE NOTES FILENAME : "+root_dir()+"/data/Release-Notes-"+request.args.get('project_name')+"-"+request.args.get('release_tag')+".html")
    if os.path.exists(root_dir()+'/data/Release-Notes-'+request.args.get('project_name')+'-'+request.args.get('release_tag')+'.html'):
       content = open(root_dir()+'/data/Release-Notes-'+request.args.get('project_name')+'-'+request.args.get('release_tag')+'.html','r').read()
       return Response(content, mimetype="text/html")
    else:
        return make_response(jsonify({'error':'Not Found'}), 400)

@application.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    application.jinja_env.auto_reload = True
    application.config['TEMPLATES_AUTO_RELOAD'] = True
    application.run(debug=True,extra_files = [root_dir()+'/data/Release-Notes-*'])
