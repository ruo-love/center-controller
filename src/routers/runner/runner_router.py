import os

from bson import json_util
from flask import Blueprint, jsonify, request, current_app as app
from src.common.helper import get_uuid
from src.common.jwt import SECRET_KEY, token_required
from src.common.secript import RunProject
import json
from src.config.server_config import scrapyd_path

# 创建运行蓝图
runner_bp = Blueprint('runner', __name__, url_prefix='/api')


# 定义路由： 创建运行日志
@runner_bp.route('/runner', methods=['POST'])
@token_required
def create_runner():
    data = request.json
    project_id = data.get('project_id')
    user_id = data.get('user_id')
    run_time = data.get('run_time')
    status = 'pending'
    if project_id and user_id and run_time and status:
        runner_collection = app.db['runner']
        runner_data = {
            '_id': get_uuid(),
            'project_id': project_id,
            'user_id': user_id,
            'run_time': run_time,
            'status': status
        }
        result = runner_collection.insert_one(runner_data)
        return jsonify({'message': 'Runner created successfully', 'runner_id': str(result)}), 201
    else:
        return jsonify({'error': 'Missing fields'}), 400


# 定义路由：获取所有运行日志
@runner_bp.route('/runner/all', methods=['GET'])
@token_required
def get_runners(decoded_token):
    runner_collection = app.db['runner']
    pipeline_projects = [
        {
            '$lookup': {
                'from': 'projects',  # 关联的集合名
                'localField': 'project_id',  # runner_collection 中的字段
                'foreignField': '_id',  # project_collection 中的字段
                'as': 'project'  # 存储关联信息的字段名
            }
        },
        {
            '$unwind': '$project'  # 展开关联信息
        }
    ]
    pipeline_users = [
        {
            '$lookup': {
                'from': 'users',  # 关联的集合名
                'localField': 'user_id',  # runner_collection 中的字段
                'foreignField': '_id',  # project_collection 中的字段
                'as': 'user'  # 存储关联信息的字段名
            }
        },
        {
            '$unwind': '$user'  # 展开关联信息
        },
        {
            '$project': {
                'user.password': 0  # 排除 user 文档中的 password 字段
            }
        }
    ]

    # 执行聚合查询
    cursor = runner_collection.aggregate(pipeline_projects + pipeline_users)
    results = list(cursor)

    return {'data': results, 'message': '获取进程列表成功'}


# 定义路由：根据user_id获取运行日志
@runner_bp.route('/runner', methods=['GET'])
@token_required
def get_runner(user_id, decoded_token):
    runner_collection = app.db['runner']
    # 获取装饰器中存储的用户信息
    user_id = decoded_token.get('_id')
    runner = runner_collection.find({'user_id': user_id})
    return {'data': runner}


# 定义路由：更新运行日志状态
@runner_bp.route('/runner/<runner_id>', methods=['PUT'])
@token_required
def update_runner(runner_id):
    data = request.json
    runner_collection = app.db['runner']
    runner = runner_collection.find_one({'_id': runner_id})
    if runner:
        runner_collection.update_one({'_id': runner_id}, {'$set': data})
        return jsonify({'message': 'Runner updated successfully'}), 200
    else:
        return jsonify({'error': 'Runner not found'}), 404


# 定义路由：获取爬虫 output文件夹内容
@runner_bp.route('/runner/<runner_id>/output', methods=['GET'])
@token_required
def get_runner_output(runner_id, decoded_token):
    runner_collection = app.db['runner']
    runner = runner_collection.find_one({'_id': runner_id})
    projects_collection = app.db['projects']
    project = projects_collection.find_one({'_id': runner['project_id']})
    if project['type'] == 'spider':
        file_data = []
        output_path = f'{scrapyd_path}\output\\{project["project_name"]}Output\\{runner_id}'
        print(output_path)
        for root, dirs, files in os.walk(output_path):
            for file in files:
                # 输出文件路径
                output_file = os.path.join(root, file)
                file_data.append(output_file)
        return jsonify({'message': '获取资源成功', 'data': file_data[0]}), 200
    else:
        return jsonify({'message': 'Project need a spider'}), 200


# 定义路由：获取爬虫 logs文件夹内容
@runner_bp.route('/runner/<runner_id>/log', methods=['GET'])
@token_required
def get_runner_logs(runner_id, decoded_token):
    runner_collection = app.db['runner']
    runner = runner_collection.find_one({'_id': runner_id})
    projects_collection = app.db['projects']
    project = projects_collection.find_one({'_id': runner['project_id']})

    if project['type'] == 'spider':
        output_file = ''
        output_path = f'{scrapyd_path}\logs\\{project["project_name"]}\\{project["project_name"]}'
        for root, dirs, files in os.walk(output_path):
            for file in files:
                # 输出文件路径
                print(runner['jobid'] in file)
                if (runner['jobid'] in file):
                    output_file = os.path.join(root, file)
                    break
        try:
            with open(output_file, 'r',encoding='utf-8') as log_file:
                log_content = log_file.read()
            return jsonify({'message': 'Project logs', 'data': log_content}), 200
        except FileNotFoundError:
            return jsonify({'error': 'Log file not found'})
    else:
        return jsonify({'message': 'Project need a spider'}), 200
