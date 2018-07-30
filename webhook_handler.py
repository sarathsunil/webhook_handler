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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
application = Flask(__name__)
issues = [
    {
        'id': 1,
        'title': u'Learn docker',
        'description': u'Need to compose build and ship',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn DevOps',
        'description': u'Need to find a good DevOps tutorial on the web',
        'done': False
    }
]

#@application.route('/commits/api/v1.0/releasenotes/<project_id>', methods=['GET'])
def html_render(project_id,commit_message,author,project_name,commit_hash):
        writer = open('/home/ubuntu/webhook_handler/data/releasenote_'+commit_hash+'.html','w')
        writer.write(render_template('template.html', project_id=project_id, committ_message=commit_message,committer=author,project_name=project_name,committ_hash=commit_hash))
        writer.close()
        return render_template('template.html', project_id=project_id, committ_message=commit_message,committer=author,project_name=project_name,committ_hash=commit_hash)
def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))
def get_latest_releasenotes():  # pragma: no cover
    try:
        # list all the files in the directory
        directory = '/home/ubuntu/webhook_handler/data/'
        files = os.listdir('/home/ubuntu/webhook_handler/data/')
        # remove all file names that don't match partial_file_name string
        #files = filter(lambda x: x.find(partial_file_name) > -1, files)
        # create a dict that contains list of files and their modification timestamps
        name_n_timestamp = dict([(x, os.stat(directory+x).st_mtime) for x in files])
        # return the file with the latest timestamp
        newest= max(name_n_timestamp, key=lambda k: name_n_timestamp.get(k))
        return open('/home/ubuntu/webhook_handler/data/'+newest,'r').read()
    except IOError as exc:
        #logger.error("Redirection error")
        return str(exc)
@application.route('/commits/api/v1.0/releasenotes/latest/', methods=['GET'])
def metrics():  # pragma: no cover
    content = get_latest_releasenotes()
    return Response(content, mimetype="text/html")

@application.route('/todo/api/v1.0/releasenotes', methods=['POST'])
def get_tasks():
    #writer = open('cache-writer.txt','w')
    #writer.write(tasks)
    print request.headers
    print request.data
    data =  json.loads(request.data)
    if 'project_id' in data.keys():
        logger.info("Project Id: "+str(data['project_id']))
        logger.info("Project Name: "+data['project']['name'])
        logger.info("Commit Message: "+str(data['commits'][0]['message']))
        logger.info("Author: "+data['commits'][0]['author']['name']+"<"+data['commits'][0]['author']['email']+">")
        print html_render(str(data['project_id']),data['commits'][0]['message'],data['commits'][0]['author']['name']+"<"+data['commits'][0]['author']['email']+">",data['project']['name'], data['commits'][0]['id'])
        return jsonify({'project_id': data['project_id']})
    else:
        return jsonify({'project_id': 'Not Found'})

@application.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    application.jinja_env.auto_reload = True
    application.config['TEMPLATES_AUTO_RELOAD'] = True
    application.run(debug=True,extra_files = ['/home/ubuntu/webhook_handler/data/releasenotes*'])
