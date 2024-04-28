from flask import Blueprint, jsonify, request, current_app as app
from src.common.helper import get_uuid

# 创建用户蓝图
user_bp = Blueprint('user', __name__)


# 定义路由：获取所有用户
@user_bp.route('/users', methods=['GET'])
def get_users():
    users_collection = app.db['users']
    users = list(users_collection.find())
    print(users)
    return {'users': users}


# 定义路由：创建用户
@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')

    if username and email:
        users_collection = app.db['users']
        user_data = {
            '_id': get_uuid(),
            'username': username,
            'email': email
        }
        result = users_collection.insert_one(user_data)
        return jsonify({'message': 'User created successfully', 'user_id': str(result.inserted_id)}), 201
    else:
        return jsonify({'error': 'Missing fields'}), 400


# 根据用户ID获取用户信息
@user_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    users_collection = app.db['users']
    user = users_collection.find_one({'_id': user_id})
    if user:
        return jsonify(user)
    else:
        return jsonify({'error': 'User not found'}), 404
