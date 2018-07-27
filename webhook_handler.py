#!usr/bin/python
import json
import jinja2
import os
from flask import Flask, jsonify, render_template
from flask import abort
from flask import make_response
from flask import request
import logging
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

@application.route('/todo/api/v1.0/taskdetails', methods=['POST'])
def get_tas():
    writer = open('cache-writer.txt','w')
    writer.write(tasks)
    return jsonify({'tasks': tasks})


@application.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == int(task_id)]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@application.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    print request.json
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201
@application.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
if __name__ == '__main__':
    application.run(debug=True)
