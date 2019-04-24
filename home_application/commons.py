# -*- coding: utf-8 -*-
import base64
import json
import time
from datetime import datetime
from functools import wraps

import settings
from blueking.component.client import ComponentClient
from blueking.component.shortcuts import get_client_by_request


def api_client(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        param = func(*args, **kwargs)
        client_module = getattr(args[1], args[0].MODULE_NAME)
        clinet_func = getattr(client_module, func.__name__)
        api_result = clinet_func(param)
        return api_result

    return wrapper


class CcApiAdapter(object):
    MODULE_NAME = 'cc'

    @classmethod
    @api_client
    def search_host(cls, client, page_start=0, page_limit=200, sort='bk_host_id', *args, **kwargs):
        """
        主机查询接口
        ip示例
        "ip": {
            "data": ["10.0.1.10", "10.0.1.11"],
            "exact": 1,
            "flag": "bk_host_innerip|bk_host_outerip"
        }
        condition是数组
        [{
            "field": "bk_inst_id",
            "operator": "$eq",
            "value": 76
        }]
        :param request:
        :param condition:
        :param page_start:
        :param page_limit:
        :param sort:
        :return:
        """
        # client = get_client_by_request(request)
        param = {
            "ip": {
                "data": kwargs.get('ip') or [],
                "exact": 1,
                "flag": "bk_host_innerip|bk_host_outerip"
            },
            "condition": [
                {
                    "bk_obj_id": "host",
                    "fields": [],
                    "condition": kwargs.get('host') or []
                },
                {
                    "bk_obj_id": "module",
                    "fields": [],
                    "condition": kwargs.get('module') or []
                },
                {
                    "bk_obj_id": "set",
                    "fields": [],
                    "condition": kwargs.get('set') or []
                },
                {
                    "bk_obj_id": "biz",
                    "fields": [],
                    "condition": kwargs.get('biz') or []
                },
                {
                    "bk_obj_id": "object",
                    "fields": [],
                    "condition": kwargs.get('object') or []
                }
            ],
            "page": {
                "start": page_start,
                "limit": page_limit,
                "sort": sort
            },
            "pattern": ""
        }
        # result = client.cc.search_host(param)
        return param

    @classmethod
    @api_client
    def search_business(cls, *args, **kwargs):
        """
        查询业务接口
        :param args:
        :param kwargs:
        :return:
        """
        param = {
            "fields": [
            ],
            "condition": kwargs or {},
            "page": {
                "start": 0,
                "limit": 10,
                "sort": ""
            }
        }
        return param

    @classmethod
    @api_client
    def search_set(cls, *args, **kwargs):
        """
        condition示例
        "condition": {
            "bk_set_name": "test"
        }
        :param args:
        :param kwargs:
        :return:
        """
        param = {
            "bk_biz_id": kwargs.get('bk_biz_id'),
            "fields": kwargs.get('fields', []),
            "condition": kwargs.get('condition', {}),
            "page": {
                "start": kwargs.get('start', 0),
                "limit": kwargs.get('limit', 100),
                "sort": "bk_set_name"
            }
        }

        return param

    @classmethod
    @api_client
    def search_module(cls, *args, **kwargs):
        param = {
            "fields": kwargs.get('fields', []),
            "condition": kwargs.get('condition', {}),
            "page": {
                "start": kwargs.get('start', 0),
                "limit": kwargs.get('limit', 100),
                "sort": "bk_set_name"
            }
        }

        return param


class JobApiAdapter(object):
    MODULE_NAME = 'job'

    @classmethod
    @api_client
    def fast_execute_script(cls, client, bk_biz_id, ip_list, **kwargs):
        """
        快速执行脚本
        script_type	int	否	脚本类型：1(shell脚本)、2(bat脚本)、3(perl脚本)、4(python脚本)、5(Powershell脚本)
        ip_list: {
            "bk_cloud_id": 0,
            "ip": "10.0.0.1"
        },
        :param request:
        :param ip_list:
        :param kwargs:
        :return:
        """
        param = {
            "bk_biz_id": bk_biz_id,
            "script_content": base64.b64encode(kwargs.get('script_content') or ""),
            "script_param": base64.b64encode(kwargs.get('script_param') or ""),
            "script_timeout": 1000,
            "account": kwargs.get('account') or "root",
            "is_param_sensitive": 0,
            "script_type": 1,
            "ip_list": ip_list,
        }

        if kwargs.get('script_id'):
            param.update({"script_id": kwargs.get('script_id')})

        return param

    @classmethod
    @api_client
    def get_job_instance_status(cls, client, bk_biz_id, instance_id):
        param = {
            "bk_biz_id": bk_biz_id,
            "job_instance_id": instance_id
        }

        return param

    @classmethod
    @api_client
    def get_job_instance_log(cls, client, bk_biz_id, job_instance_id):
        param = {
            "bk_biz_id": bk_biz_id,
            "job_instance_id": job_instance_id,
        }

        return param

    @classmethod
    @api_client
    def get_job_detail(cls, *args, **kwargs):
        param = {
            "bk_biz_id": kwargs['bk_biz_id'],
            "bk_job_id": kwargs['bk_job_id'],
        }

        return param

    @classmethod
    @api_client
    def execute_job(cls, *args, **kwargs):
        bk_biz_id = kwargs['bk_biz_id']
        bk_job_id = kwargs['bk_job_id']
        job_detail_result = cls.get_job_detail(*args, **kwargs)
        job_info = job_detail_result['data']
        step = job_info['steps'][0]
        step.pop('script_content')
        step.pop('script_id')
        step.setdefault('script_param', base64.b64encode(kwargs.get('script_param', "")))
        step['ip_list'] = kwargs['ip_list']

        param = {
            "bk_biz_id": bk_biz_id,
            "bk_job_id": bk_job_id,
            "steps": [step],
        }

        # if 'global_vars' in job_info:
        #     global_vars = job_info['global_vars'][0]
        #     global_vars['ip_list'] = kwargs['ip_list']
        #     param["global_vars"] = [global_vars],

        return param

    @classmethod
    @api_client
    def fast_execute_sql(cls, *args, **kwargs):
        param = {
            "bk_biz_id": kwargs['bk_biz_id'],
            "script_content": base64.b64encode(kwargs.get('script_content', '')),
            "script_timeout": 1000,
            "db_account_id": int(kwargs.get('db_account_id') or 0),
            "ip_list": kwargs.get('ip_list') or []
        }
        if kwargs['script_id']:
            param['script_id'] = kwargs['script_id']

        return param

    @classmethod
    @api_client
    def fast_push_file(cls, *args, **kwargs):
        username = args[0]
        param = {
            "bk_biz_id": kwargs['bk_biz_id'],
            "file_target_path": kwargs['file_path'],
            "file_source": [
                {
                    "files": kwargs['file_source_path'],
                    "account": username,
                    "ip_list": kwargs.get('ip_list') or [],
                }
            ],
            "ip_list": kwargs.get('ip_list') or [],
            "account": username,
        }

        return param


def host_key(ip, bk_cloud_id):
    return '%s|%s' % (ip, bk_cloud_id)


def get_job_log_content(log_info):
    if log_info['result'] and log_info['data'][0]['status'] == 3:
        log_dict = {}
        for step in log_info['data'][0]['step_results']:
            for ip_log in step['ip_logs']:
                log_content = ip_log['log_content'][:-1]
                log_dict[host_key(ip_log['ip'], ip_log['bk_cloud_id'])] = {
                    'ip': ip_log['ip'],
                    'bk_cloud_id': ip_log['bk_cloud_id'],
                    'log_content': log_content,
                    'status': step['ip_status']
                }

        if log_dict:
            return True, log_dict

    return False, '作业未执行成功'


def execute_script_and_get_log(client, bk_biz_id, ip_list, script_content):
    """
    执行脚本并获取执行成功的结果
    返回的对象{(ip, bk_cloud_id,): log_content}
    :return:
    """
    execute_param = {
        'bk_biz_id': bk_biz_id,
        'ip_list': ip_list,
        'script_content': script_content,
    }
    result = JobApiAdapter.fast_execute_script(client, **execute_param)
    if not result['result']:
        return False, "作业未执行成功"

    log_param = {
        'job_instance_id': result['data']['job_instance_id'],
        'bk_biz_id': bk_biz_id,
    }
    log_info = JobApiAdapter.get_job_instance_log(client, **log_param)
    is_success, log_dict = get_job_log_content(log_info)
    i = 0
    while not is_success and log_info['data'][0]['status'] == 2:
        i = i + 1
        if i > 5:
            break

        time.sleep(2)
        log_info = JobApiAdapter.get_job_instance_log(client, **log_param)
        is_success, log_dict = get_job_log_content(log_info)

    return is_success, log_dict


def execute_job_and_get_log(client, bk_biz_id, ip_list, job_id):
    """
    执行脚本并获取执行成功的结果
    返回的对象{(ip, bk_cloud_id,): log_content}
    :return:
    """
    execute_param = {
        'bk_biz_id': bk_biz_id,
        'ip_list': ip_list,
        'bk_job_id': job_id,
    }
    result = JobApiAdapter.execute_job(client, **execute_param)
    if not result['result']:
        return False, "作业未执行成功"

    log_param = {
        'job_instance_id': result['data']['job_instance_id'],
        'bk_biz_id': bk_biz_id,
    }
    log_info = JobApiAdapter.get_job_instance_log(client, **log_param)
    is_success, log_dict = get_job_log_content(log_info)
    i = 0
    while not is_success and log_info['data'][0]['status'] == 2:
        i = i + 1
        if i > 5:
            break

        time.sleep(2)
        log_info = JobApiAdapter.get_job_instance_log(client, **log_param)
        is_success, log_dict = get_job_log_content(log_info)

    return is_success, log_dict


def time_to_str(date_time):
    return str(date_time)


def str_to_time(date_tiem):
    return datetime.strptime(date_tiem, '%Y-%m-%d %H:%M:%S')
