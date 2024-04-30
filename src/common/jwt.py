import jwt
import datetime
from functools import wraps
from flask import request, jsonify

SECRET_KEY = 'zero'


# 装饰器：验证 JWT 的有效性
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            kwargs['decoded_token'] = data  # 将解密后的数据传递给路由函数的关键字参数
        except:
            return jsonify({'error': 'Token is invalid'}), 401

        return f(*args, **kwargs)

    return decorated


# 装饰器：管理员权限验证#
def role_required(required_role):
   def decorator(func):
       @wraps(func)
       def wrapper(*args, **kwargs):
           # 获取解密后的 token 数据
           decoded_token = kwargs.get('decoded_token')
           if not decoded_token:
               return jsonify({'error': 'Token is missing or invalid'}), 401
           # 假设 token 中包含用户角色信息
           user_roles = decoded_token.get('roles')
           if required_role not in user_roles:
               return jsonify({'error': 'Insufficient permissions'}), 403
           return func(*args, **kwargs)
       return wrapper
   return decorator
