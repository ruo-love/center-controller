import subprocess
import os
import json
import requests
from src.config.server_config import scrapyd_host
from flask import Blueprint, jsonify, request, current_app as app


class RunProject:
    def __init__(self, project, runner_id):
        self.project = project
        self.project_id = project.get('_id')
        self.project_name = project.get('project_name')
        self.project_display_name = project.get('project_display_name')
        self.description = project.get('description')
        self.type = project.get('type')
        self.source_path = project.get('source_path')
        self.terminal_path = project.get('terminal_path')
        self.options = project.get('options')
        self.create_time = project.get('create_time')
        self.update_time = project.get('update_time')
        self.github_url = project.get('github_url')
        self.runner_id = runner_id

    def run(self):
        print('开始检测脚本类型')
        if self.type == 'python':
            try:
                # 构建基本的命令列表
                command = ['cmd', '/c', 'python', self.source_path]
                # 使用 extend() 方法将选项列表添加到命令列表末尾
                command.extend(self.options)
                print(f'运行python脚本:${command}')
                # 使用 subprocess 调用命令行运行脚本
                subprocess.run(command, cwd=self.terminal_path)

            except subprocess.CalledProcessError as e:
                print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}")
                print(f"Output: {e.output.decode() if e.output else ''}")
            except Exception as e:
                print(f"An error occurred: {e}")
        if self.type == 'spider':
            print(f'运行scrapy爬虫')
            try:
                # 构建请求体
                data = {
                    'project': self.project_name,
                    'spider': self.project_name,
                    'runner_id': self.runner_id
                }
                # self.options
                data.update(self.options)
                # 发送请求
                response = requests.post(scrapyd_host, data=data)
                runner_collection = app.db['runner']
                jobid = response.json()["jobid"]
                update_data = {
                    "jobid": jobid
                }
                runner_collection.update_one({'_id': self.runner_id}, {'$set': update_data})



            except subprocess.CalledProcessError as e:
                print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}")
                print(f"Output: {e.output.decode() if e.output else ''}")
            except Exception as e:
                print(f"An error occurred: {e}")
