from flask import Blueprint, jsonify, request, current_app as app
from src.common.helper import get_uuid
from src.common.jwt import SECRET_KEY, token_required
import jwt
import datetime
# 创建用户蓝图
auth_bp = Blueprint('auth', __name__)

# 定义路由：用户登录 返回token 用户信息
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    users_collection = app.db['users']
    user = users_collection.find_one({'email': email, 'password': password})
    if user:
        token = jwt.encode({'email': email, '_id': user['_id'], 'roles':user['roles'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)},
                           SECRET_KEY, algorithm='HS256')
        return jsonify({'message': 'Login successful', "data": user, "token": token}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


# 定义路由：创建权限角色
@auth_bp.route('/roles', methods=['POST'])
@token_required
def create_role():
    data = request.json
    role_name = data.get('role_name')
    permissions = data.get('permissions')
    if role_name and permissions:
        roles_collection = app.db['roles']
        role_data = {
            '_id': get_uuid(),
            'role_name': role_name,
            'permissions': permissions
        }
        result = roles_collection.insert_one(role_data)
        return jsonify({'message': 'Role created successfully', 'role_id': str(result)}), 201
    else:
        return jsonify({'error': 'Missing fields'}), 400

# 定义路由：获取所有权限角色
@auth_bp.route('/roles', methods=['GET'])
@token_required
def get_roles():
    roles_collection = app.db['roles']
    roles = list(roles_collection.find())
    return {'data': roles}

# 定义路由：获取权限数据列表
@auth_bp.route('/permissions', methods=['GET'])
@token_required
def get_permissions():
    permissions_collection = app.db['permissions']
    permissions = list(permissions_collection.find())
    return {'permissions': permissions}

# 定义路由：删除权限角色
@auth_bp.route('/roles/<role_id>', methods=['DELETE'])
@token_required
def delete_role(role_id):
    roles_collection = app.db['roles']
    role = roles_collection.find_one({'_id': role_id})
    if role:
        roles_collection.delete
        return jsonify({'message': 'Role deleted successfully'}), 200
    else:
        return jsonify({'error': 'Role not found'}), 404
