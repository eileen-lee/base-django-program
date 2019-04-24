# -*- coding: utf-8 -*-
import datetime
import json
import time

import requests
from django.forms import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from account.decorators import login_exempt
from blueking.component.shortcuts import get_client_by_request
from common.mymako import render_mako_context
from common.mymako import render_json
from conf.default import APP_ID, APP_TOKEN, BK_PAAS_HOST
# from home_application.celery_tasks import monitor_task
from home_application.commons import CcApiAdapter, JobApiAdapter
# from home_application.models import MonitorItem, MonitorData


def home(request):
    """
    首页
    """
    return render_mako_context(request, '/home_application/home.html')


def status(request):
    """
    主机状态
    """
    return render_mako_context(request, '/home_application/status.html')


def dev_guide(request):
    """
    开发指引
    """
    return render_mako_context(request, '/home_application/dev_guide.html')


def contactus(request):
    """
    联系我们
    """
    return render_mako_context(request, '/home_application/contact.html')


def test(request):
    """
    测试
    """
    return render_mako_context(request, '/home_application/test.html')


@csrf_exempt
@require_http_methods(["POST"])
def get_biz_list(request):
    client = get_client_by_request(request)
    param = json.loads(request.body)
    result = CcApiAdapter.search_business(client, **param)
    return render_json(result)


@csrf_exempt
@require_http_methods(["POST"])
def get_host_list(request):
    client = get_client_by_request(request)
    param = json.loads(request.body)
    result = CcApiAdapter.search_host(client, **param)
    monitor_item_list = MonitorItem.objects.filter(bk_biz_id=param['biz'][0]['value'])
    for item in result['data']['info']:
        filter_list = filter(lambda x: item['host']['bk_host_innerip']==x.ip, monitor_item_list)
        if len(filter_list) > 0:
            item['host']['is_exist'] = True

    return render_json(result)


@csrf_exempt
@require_http_methods(["POST"])
def search_performance(request):
    client = get_client_by_request(request)
    script_content = """MEMORY=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
DISK=$(df -h | awk '$NF=="/"{printf "%s", $5}')
CPU=$(top -bn1 | grep load | awk '{printf "%.2f%%", $(NF-2)}')
DATE=$(date "+%Y-%m-%d %H:%M:%S")
echo -e "$DATE|$MEMORY|$DISK|$CPU"
"""
    param = json.loads(request.body)
    result = JobApiAdapter.fast_execute_script(client, script_content=script_content, **param)
    if result['result']:
        get_job_log_param = {
            'job_instance_id': result['data']['job_instance_id'],
            'bk_biz_id': param['bk_biz_id'],
        }
        for i in xrange(3):
            log_info = JobApiAdapter.get_job_instance_log(client, **get_job_log_param)
            if log_info['result'] and log_info['data'][0]['is_finished'] and \
                    log_info['data'][0]['status'] == 3:
                log_content = log_info['data'][0]['step_results'][0]['ip_logs'][0]['log_content'][:-1]
                log_metrics = log_content.split('|')[1:]
                return render_json({
                    'result': True,
                    'mem': log_metrics[0],
                    'disk': log_metrics[1],
                    'cpu': log_metrics[2],
                })

            time.sleep(1.5)

    return render_json({
        'result': False,
        'message': '查询失败',
    })


@csrf_exempt
@require_http_methods(["POST"])
def toggle_monitor(request):
    """添加删除监控"""
    param = json.loads(request.body)
    monitor_item = {
        'bk_biz_id': param['bk_biz_id'],
        'ip': param['ip'],
        'bk_cloud_id': param['bk_cloud_id'],
    }
    if param['is_add']:
        instance, is_create = MonitorItem.origin_objects.get_or_create(**monitor_item)
        if not is_create:
            instance.is_deleted = False
            instance.save()
    else:
        instance = MonitorItem.objects.filter(**monitor_item)[0]
        instance.delete()

    return render_json({
        'result': True
    })


@csrf_exempt
@require_http_methods(["GET"])
def get_monitor_list(request):
    param = json.loads(request.GET)
    obj_list = MonitorItem.objects.filter(**param)
    result_list = []
    for obj in obj_list:
        result_list.append(model_to_dict(obj))

    return render_json({
        'result': True,
        'info': result_list
    })


@csrf_exempt
@require_http_methods(["POST"])
def get_monitor_host(request):
    param = json.loads(request.body)
    monitor_list = MonitorItem.objects.filter(bk_biz_id=param['bk_biz_id'])
    if param['ip_list']:
        monitor_list = monitor_list.filter(ip__in=param['ip_list'])

    monitor_list = monitor_list.order_by('id')
    return render_json({
        'data': [model_to_dict(obj) for obj in monitor_list],
        'result': True,
    })


@csrf_exempt
@require_http_methods(["POST"])
def get_chart_data(request):
    param = json.loads(request.body)
    item = MonitorItem.objects.get(bk_biz_id=param['bk_biz_id'], ip=param['ip'])

    t = datetime.datetime.now() + datetime.timedelta(hours=-1)
    performance_data = MonitorData.objects.filter(monitor_item=item, create_time__gte=t)
    xAxis = []
    cpu_data = []
    mem_data = []
    disk_data = []
    for data in performance_data:
        xAxis.append(str(data.create_time))
        cpu_data.append(data.cpu)
        mem_data.append(data.mem)
        disk_data.append(data.disk)

    return render_json({
        'result': True,
        'chart_data': {
            "xAxis": xAxis,
            "series": [
                {
                    "name": "cpu",
                    "type": "line",
                    "data": cpu_data
                },{
                    "name": "mem",
                    "type": "line",
                    "data": mem_data
                },{
                    "name": "disk",
                    "type": "line",
                    "data": disk_data
                },
            ]
        },
    })
