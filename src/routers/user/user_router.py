from flask import Blueprint, jsonify, request, current_app as app
from src.common.helper import get_uuid
from src.common.jwt import token_required
# 创建用户蓝图
user_bp = Blueprint('user', __name__)


# 定义路由：获取所有用户
@user_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    users_collection = app.db['users']
    users = list(users_collection.find())
    print(users)
    return {'users': users}


# 定义路由：创建用户
@user_bp.route('/users', methods=['POST'])
@token_required
def create_user():
    data = request.json
    password = data.get('password')
    email = data.get('email')
    roles = ['admin', 'user']

    if password and email:
        users_collection = app.db['users']
        user_data = {
            '_id': get_uuid(),
            'email': email,
            'password': password,
            'roles': roles
        }
        result = users_collection.insert_one(user_data)
        return jsonify({'message': 'User created successfully', 'user_id': str(result)}), 201
    else:
        return jsonify({'error': 'Missing fields'}), 400


# 根据用户ID获取用户信息
@user_bp.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    users_collection = app.db['users']
    user = users_collection.find_one({'_id': user_id})
    if user:
        return jsonify(user)
    else:
        return jsonify({'error': 'User not found'}), 404


# 根据用户ID更新用户信息
@user_bp.route('/users/<user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    data = request.json
    users_collection = app.db['users']
    user = users_collection.find_one({'_id': user_id})
    if user:
        users_collection.update_one({'_id': user_id}, {'$set': data})
        return jsonify({'message': 'User updated successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404

# 根据用户ID删除用户
@user_bp.route('/users/<user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    users_collection = app.db['users']
    user = users_collection.find_one({'_id': user_id})
    if user:
        users_collection.delete_one({'_id': user_id})
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404