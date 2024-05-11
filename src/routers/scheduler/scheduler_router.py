import datetime
import os
from flask import Blueprint, jsonify, request, current_app as app
from src.common.helper import get_uuid
from src.common.jwt import SECRET_KEY, token_required, role_required
from src.common.secript import RunProject
from src.config.server_config import scrapyd_path

from apscheduler.schedulers.background import BackgroundScheduler

# scheduler = BlockingScheduler()
# # 使用 cron 表达式，设置每周星期六（周六是星期的第6天，所以设置 day_of_week=5）的特定时间（12:36:40）执行任务
# # scheduler.add_job(job, 'cron', day_of_week=5, hour=12, minute=36, second=40)
#
# try:
#     scheduler.start()
# except KeyboardInterrupt:
#     scheduler.shutdown()
# 创建用户蓝图
scheduler_bp = Blueprint('scheduler', __name__, url_prefix='/api')


# 定义路由：增加定时任务
@scheduler_bp.route('/scheduler', methods=['POST'])
@token_required
def create_scheduler(decoded_token):
    data = request.json
    project_id = data.get('project_id')
    rules = data.get('rules')
    user_id = decoded_token['_id']
    schedulers_collection = app.db['schedulers']
    scheduler_data = {
        '_id': get_uuid(),
        'project_id': project_id,
        'user_id': user_id,
        'rules': rules,
        'create_time': datetime.datetime.utcnow(),
        'status': False
    }
    schedulers_collection.insert_one(scheduler_data)
    return {'data': {}, 'message': '创建定时任务成功'}


# 定义路由：更新定时任务
@scheduler_bp.route('/scheduler/<scheduler_id>', methods=['PUT'])
@token_required
def put_scheduler(scheduler_id, decoded_token):
    schedulers_collection = app.db['schedulers']
    data = request.json
    project_id = data.get('project_id')
    rules = data.get('rules')
    status = data.get('status')

    scheduler_data = {
        'project_id': project_id,
        'rules': rules,
        'status': status
    }
    schedulers_collection.update_one({'_id': scheduler_id}, {'$set': scheduler_data})
    role = schedulers_collection.find_one({'_id': scheduler_id})
    update_scheduler_listen()
    return {'data': {}, 'message': '更新定时任务成功'}


# 定义路由：删除定时任务
@scheduler_bp.route('/scheduler/<scheduler_id>', methods=['DELETE'])
@token_required
def del_scheduler(scheduler_id, decoded_token):
    schedulers_collection = app.db['schedulers']
    schedulers_collection.delete_one({'_id': scheduler_id})
    return {'data': {}, 'message': '删除定时任务成功'}


# 定义路由：查询定时任务
@scheduler_bp.route('/scheduler', methods=['GET'])
@token_required
@role_required('admin')
def get_scheduler(decoded_token):
    schedulers_collection = app.db['schedulers']
    schedulers = list(schedulers_collection.find())
    return {'data': schedulers, 'message': '查询定时任务成功'}


# 更新定时器监听
def update_scheduler_listen():
    try:
        if hasattr(app, 'block_scheduler') and hasattr(app.block_scheduler, 'shutdown'):
            app.block_scheduler.shutdown()
        app.block_scheduler = BackgroundScheduler()
        schedulers_collection = app.db['schedulers']
        roles = list(schedulers_collection.find())
        for role in roles:
            app.block_scheduler.add_job(job, 'cron', id=str(role['_id']), args=[role], **role['rules'])
        app.block_scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        # 捕获异常，停止调度器
        print(KeyboardInterrupt, SystemExit)


def job(role):
    print("定时任务执行中...", role)
    # 在这里编写你的任务逻辑
