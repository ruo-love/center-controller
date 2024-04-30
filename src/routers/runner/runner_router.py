from flask import Blueprint, jsonify, request, current_app as app
from src.common.helper import get_uuid
from src.common.jwt import SECRET_KEY, token_required
from src.common.secript import RunProject

# 创建运行蓝图
runner_bp = Blueprint('runner', __name__)

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
    runners = list(runner_collection.find())
    return {'data': runners}

# 定义路由：根据user_id获取运行日志
@runner_bp.route('/runner', methods=['GET'])
@token_required
def get_runner(user_id,decoded_token):
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