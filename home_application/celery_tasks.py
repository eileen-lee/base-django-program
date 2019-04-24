# -*- coding: utf-8 -*-
"""
celery 任务示例

本地启动celery命令: python  manage.py  celery  worker  --settings=settings
周期性任务还需要启动celery调度命令：python  manage.py  celerybeat --settings=settings
"""
import datetime
import json
import time

import requests
from celery import task, chain
from celery.schedules import crontab
from celery.task import periodic_task
from django.forms import model_to_dict
from django.http import JsonResponse

import settings
from blueking.component.client import ComponentClient, ComponentClientWithSignature, BaseComponentClient
from blueking.component.shortcuts import get_client_by_request
from common.log import logger
from home_application.commons import JobApiAdapter, get_job_log_content, host_key, execute_script_and_get_log, \
    str_to_time


# client = ComponentClient(
#     bk_app_code=settings.APP_ID,
#     bk_app_secret=settings.APP_TOKEN,
#     common_args={'bk_username': 'admin'}
# )


@task()
def async_task(x, y):
    """
    定义一个 celery 异步任务
    """
    logger.error(u"celery 定时任务执行成功，执行结果：{:0>2}:{:0>2}".format(x, y))
    return x + y


def execute_task():
    """
    执行 celery 异步任务

    调用celery任务方法:
        task.delay(arg1, arg2, kwarg1='x', kwarg2='y')
        task.apply_async(args=[arg1, arg2], kwargs={'kwarg1': 'x', 'kwarg2': 'y'})
        delay(): 简便方法，类似调用普通函数
        apply_async(): 设置celery的额外执行选项时必须使用该方法，如定时（eta）等
                      详见 ：http://celery.readthedocs.org/en/latest/userguide/calling.html
    """
    now = datetime.datetime.now()
    logger.error(u"celery 定时任务启动，将在60s后执行，当前时间：{}".format(now))
    # 调用定时任务
    async_task.apply_async(args=[now.hour, now.minute], eta=now + datetime.timedelta(seconds=60))


@periodic_task(run_every=crontab(minute='*', hour='*', day_of_week="*"))
def get_time():
    """
    celery 周期任务示例

    run_every=crontab(minute='*/5', hour='*', day_of_week="*")：每 5 分钟执行一次任务
    periodic_task：程序运行时自动触发周期任务
    """
    execute_task()
    now = datetime.datetime.now()
    logger.error(u"celery 周期任务调用成功，当前时间：{}".format(now))


@task()
def custom_fun1(**kwargs):
    a = kwargs.get('a')
    print a
    return a


@task()
def custom_fun2(per_result, **kwargs):
    b = kwargs.get('b')
    print per_result + '+' + b


@task()
def chain_task(fun1_param, fun2_param):
    chain(
        custom_fun1.s(**fun1_param),
        custom_fun2.s(**fun2_param)
    ).delay()


# @periodic_task(run_every=crontab(minute='*', hour='*', day_of_week="*"))
# def data_collect():
#     try:
#         ls_instance = CookieData.objects.all().order_by('-create_time')[0]
#         common_args = {
#             'bk_token': ls_instance.value,
#         }
#         client = ComponentClient(settings.APP_ID, settings.APP_TOKEN, common_args=common_args)
#     except:
#         pass
#
#     script_content = '''MEMORY=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
# DISK=$(df -h | awk '$NF=="/"{printf "%s", $5}')
# CPU=$(top -bn1 | grep load | awk '{printf "%.2f%%", $(NF-2)}')
# DATE=$(date "+%Y-%m-%d %H:%M:%S")
# echo -e "$DATE|$MEMORY|$DISK|$CPU"'''
#     all_host = MonitorHost.objects.all()
#     groups = {}
#     for host in all_host:
#         groups.setdefault(str(host.bk_biz_id), []).append({
#             'ip': host.ip,
#             'bk_cloud_id': host.bk_cloud_id
#         })
#
#     for group_key in groups.keys():
#         is_success, log_dict = execute_script_and_get_log(client, group_key, groups[group_key], script_content)
#         if not is_success:
#             continue
#
#         for log_info in log_dict.values():
#             try:
#                 the_host = filter(lambda x: x.ip == log_info['ip'] and x.bk_cloud_id == log_info['bk_cloud_id'], all_host)[0]
#                 metrics = log_info['log_content'].split('|')
#                 host_data = {
#                     'create_time': str_to_time(metrics[0]),
#                     'mem': float(metrics[1][:-1]),
#                     'disk': float(metrics[1][:-1]),
#                     'cpu': float(metrics[1][:-1]),
#                     'host': the_host,
#                 }
#                 HostData.objects.create(**host_data)
#             except:
#                 pass


# @periodic_task(run_every=crontab(minute='*/5', hour='*', day_of_week="*"))
# def get_job_log():
#     record_list = JobRecord.objects.filter(status='PENDING')
#     for record in record_list:
#         try:
#             get_log_result = JobApiAdapter.get_job_instance_log(client, record.bk_biz_id, record.job_instance_id)
#             is_ok, log_dict = get_job_log_content(get_log_result)
#             if is_ok:
#                 if all(map(lambda x: x['status'] == 9, log_dict.values())):
#                     record.status = "SUCCESS"
#                 else:
#                     record.status = "FAILED"
#
#                 record.log_content = json.dumps(log_dict.values())
#                 record.save()
#         except Exception as e:
#             print e
#             pass

# @periodic_task(run_every=crontab(minute='*', hour='*', day_of_week="*"))
# def monitor_task():
#     """
#     celery 周期任务示例
#
#     run_every=crontab(minute='*/5', hour='*', day_of_week="*")：每 5 分钟执行一次任务
#     periodic_task：程序运行时自动触发周期任务
#     """
#     # client = get_client_by_request(request)
#     try:
#         instance = CookieData.objects.all().order_by('-create_time')[0]
#         common_args = {
#             'bk_token': instance.value,
#         }
#         client = ComponentClient(settings.APP_ID, settings.APP_TOKEN, common_args=common_args)
#     except:
#         pass
#
#     all_monitor = MonitorHost.objects.all()
#     host_groups = {}
#     for host in all_monitor:
#         host_groups.setdefault(str(host.bk_biz_id), []).append({
#             'ip': host.ip,
#             'bk_cloud_id': host.bk_cloud_id,
#         })
#
#     execute_result = []
#     for group_key in host_groups.keys():
#         execute_param = {
#             'bk_biz_id': group_key,
#             'ip_list': host_groups[group_key],
#             'bk_job_id': 1,
#         }
#         result = JobApiAdapter.execute_job(client, **execute_param)
#         if result['result']:
#             execute_result.append({
#                 'job_instance_id': result['data']['job_instance_id'],
#                 'bk_biz_id': int(group_key),
#             })
#
#     time.sleep(2)
#     for param in execute_result:
#         log_info = JobApiAdapter.get_job_instance_log(client, **param)
#         is_success, log_dict = get_job_log_content(log_info)
#         i = 0
#         while not is_success and log_info['data'][0]['status'] == 2:
#             i += 1
#             if i > 6:
#                 break
#
#             time.sleep(2)
#             log_info = JobApiAdapter.get_job_instance_log(client, **param)
#             is_success, log_dict = get_job_log_content(log_info)
#
#         if is_success:
#             for log_ip in log_dict.keys():
#                 current_host = filter(lambda x: x.ip == log_dict[log_ip]['ip'] and x.bk_cloud_id == log_dict[log_ip]['bk_cloud_id'], all_monitor)[0]
#                 load_data = {
#                     'host': current_host,
#                     'load': float(log_dict[log_ip]['log_content'].split()[1]),
#                 }
#                 HostLoadData.objects.create(**load_data)
