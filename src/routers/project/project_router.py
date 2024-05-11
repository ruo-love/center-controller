import datetime

from flask import Blueprint, jsonify, request, current_app as app
from src.common.helper import get_uuid
from src.common.jwt import SECRET_KEY, token_required, role_required
from src.common.secript import RunProject
from src.config.server_config import scrapyd_path
import os

# 创建用户蓝图
project_bp = Blueprint('project', __name__, url_prefix='/api')


# 定义路由：获取所有项目
@project_bp.route('/project', methods=['GET'])
@token_required
def get_projects(decoded_token):
    projects_collection = app.db['projects']
    projects = list(projects_collection.find())
    return {'data': projects, 'message': '获取项目列表成功'}


# 定义路由：创建项目
@project_bp.route('/project', methods=['POST'])
@token_required
@role_required(required_role='admin')
def create_project(decoded_token):
    data = request.json
    project_name = data.get('project_name')
    project_display_name = data.get('project_display_name')
    description = data.get('description')
    type = data.get('type')
    source_path = data.get('source_path')
    terminal_path = data.get('terminal_path')
    options = data.get('options')
    create_time = datetime.datetime.utcnow()
    update_time = datetime.datetime.utcnow()
    github_url = data.get('github_url')
    if project_name and project_display_name and  description and type and source_path and terminal_path and options and create_time and update_time and github_url:
        projects_collection = app.db['projects']
        project_data = {
            '_id': get_uuid(),
            'project_name': project_name,
            'project_display_name': project_display_name,
            'description': description,
            'type': type,
            'source_path': source_path,
            'options': options,
            'create_time': create_time,
            'update_time': update_time,
            'github_url': github_url
        }
        result = projects_collection.insert_one(project_data)
        return jsonify({'message': 'Project created successfully', 'project_id': str(result)}), 201
    else:
        return jsonify({'error': 'Missing fields'}), 400


# 定义路由：获取项目详情
@project_bp.route('/project/<project_id>', methods=['GET'])
@token_required
def get_project(project_id):
    projects_collection = app.db['projects']
    project = projects_collection.find_one({'_id': project_id})
    return {'data': project}


# 定义路由：更新项目
@project_bp.route('/project/<project_id>', methods=['PUT'])
@token_required
def update_project(project_id,decoded_token):
    data = request.json
    project_name = data.get('project_name')
    project_display_name = data.get('project_display_name')
    description = data.get('description')
    type = data.get('type')

    source_path = data.get('source_path')
    options = data.get('options')
    create_time = data.get('create_time')
    update_time = data.get('create_time')
    github_url = data.get('github_url')
    if project_name and project_display_name and  description and type and source_path and options and create_time and update_time and github_url:
        projects_collection = app.db['projects']
        project_data = {
            'project_name': project_name,
            'project_display_name': project_display_name,
            'description': description,
            'type': type,
            'source_path': source_path,
            'options': options,
            'create_time': create_time,
            'update_time': update_time,
            'github_url': github_url
        }
        result = projects_collection.update_one({'_id': project_id}, {'$set': project_data})
        return jsonify({'message': 'Project updated successfully', 'project_id': str(result)}), 200
    else:
        return jsonify({'error': 'Missing fields'}), 400


# 定义路由：删除项目
@project_bp.route('/project/<project_id>', methods=['DELETE'])
@token_required
def delete_project(project_id,decoded_token):
    projects_collection = app.db['projects']
    result = projects_collection.delete_one({'_id': project_id})
    return jsonify({'message': 'Project deleted successfully', 'project_id': str(result)}), 200


# 定义路由：运行项目
@project_bp.route('/project/<project_id>/run', methods=['POST'])
@token_required
def run_project(project_id, decoded_token):
    projects_collection = app.db['projects']
    project = projects_collection.find_one({'_id': project_id})
    print(project)
    print(decoded_token)
    user_id = decoded_token['_id']
    run_time = datetime.datetime.utcnow()
    runner_collection = app.db['runner']
    _id = get_uuid()
    runner_data = {
        '_id': _id,
        'project_id': project_id,
        'user_id': user_id,
        'run_time': run_time,
    }
    runner_collection.insert_one(runner_data)
    runner = RunProject(project,_id)
    runner.run()
    return jsonify({'message': 'Project running', 'project_id': str(project)}), 200


# 定义路由：获取项目日志
@project_bp.route('/project/<project_id>/log', methods=['GET'])
@token_required
def get_project_log(project_id, decoded_token):
    projects_collection = app.db['projects']
    project = projects_collection.find_one({'_id': project_id})
    return jsonify({'message': 'Project log', 'log': project}), 200


# 定义路由：获取爬虫 output文件夹内容
@project_bp.route('/project/<project_id>/output', methods=['GET'])
@token_required
def get_project_output(project_id, decoded_token):
    projects_collection = app.db['projects']
    project = projects_collection.find_one({'_id': project_id})
    if project['type'] == 'spider':
        file_data = []
        output_path = f'{scrapyd_path}\output\\{project["project_name"]}Output'
        for root, dirs, files in os.walk(output_path):
            for file in files:
                # 输出文件路径
                output_file = os.path.join(root, file)
                file_data.append(output_file)
        return jsonify({'message': 'Project output', 'data': file_data}), 200
    else:
        return jsonify({'message': 'Project need a spider'}), 200


# 定义路由：获取爬虫 logs文件夹内容
@project_bp.route('/project/<project_id>/logs', methods=['GET'])
@token_required
def get_project_logs(project_id, decoded_token):
    projects_collection = app.db['projects']
    project = projects_collection.find_one({'_id': project_id})

    if project['type'] == 'spider':
        file_data = []
        output_path = f'{scrapyd_path}\logs\\{project["project_name"]}\\{project["project_name"]}'
        for root, dirs, files in os.walk(output_path):
            for file in files:
                # 输出文件路径
                output_file = os.path.join(root, file)
                file_data.append(output_file)
        return jsonify({'message': 'Project logs', 'data': file_data}), 200
    else:
        return jsonify({'message': 'Project need a spider'}), 200
