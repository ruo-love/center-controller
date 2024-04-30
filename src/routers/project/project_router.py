import datetime

from flask import Blueprint, jsonify, request, current_app as app
from src.common.helper import get_uuid
from src.common.jwt import SECRET_KEY, token_required,role_required
from src.common.secript import RunProject
# 创建用户蓝图
project_bp = Blueprint('project', __name__)

# 定义路由：获取所有项目
@project_bp.route('/project', methods=['GET'])
@token_required
def get_projects():
    projects_collection = app.db['projects']
    projects = list(projects_collection.find())
    return {'data': projects}

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
    if project_name and project_display_name and description and type and source_path and terminal_path and options and create_time and update_time and github_url:
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
def update_project(project_id):
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
    if project_name and project_display_name and description and type and source_path and options and create_time and update_time and github_url:
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
def delete_project(project_id):
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
    runner = RunProject(project)
    runner.run()
    return jsonify({'message': 'Project running', 'project_id': str(project)}), 200

