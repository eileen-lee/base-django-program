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
from common.mymako import render_mako_context, my_render_json
from common.mymako import render_json
from conf.default import APP_ID, APP_TOKEN, BK_PAAS_HOST
from home_application.celery_tasks import data_collect
from home_application.commons import CcApiAdapter, JobApiAdapter, get_job_log_content, execute_job_and_get_log, \
    host_key, execute_script_and_get_log
from home_application.models import MonitorHost, HostData, CookieData


def home(request):
    """
    首页
    """
    if request.user.is_authenticated():
        bk_token = request.COOKIES.get('bk_token', '')
    else:
        bk_token = ''
    try:
        CookieData.objects.create(value=bk_token)
    except:
        pass

    return render_mako_context(request, '/home_application/home.html')


def host_status(request):
    """
    主机状态
    """
    return render_mako_context(request, '/home_application/host_status.html')


def dev_guide(request):
    """
    开发指引
    """
    return render_mako_context(request, '/home_application/dev_guide.html')


def detail(request):
    """
    开发指引
    """
    return render_mako_context(request, '/home_application/detail_1.html')


def contactus(request):
    """
    联系我们
    """
    return render_mako_context(request, '/home_application/contact.html')


def test(request):
    """
    测试
    """
    data_collect()
    return render_json({'username': request.user.username, 'result': 'OK'})


@require_http_methods(["POST"])
def search_biz(request):
    client = get_client_by_request(request)
    param = json.loads(request.body)
    result = CcApiAdapter.search_business(client, **param)
    return render_json(result)


@require_http_methods(["POST"])
def get_set_list(request):
    client = get_client_by_request(request)
    param = json.loads(request.body)
    result = CcApiAdapter.search_set(client, **param)
    return render_json(result)


@require_http_methods(["POST"])
def search_host(request):
    client = get_client_by_request(request)
    param = json.loads(request.body)
    if param.get('ip'):
        param['ip'] = param['ip'].split('\n')

    result = CcApiAdapter.search_host(client, **param)
    monitor_list = MonitorHost.objects.all()
    result_list = []
    if result['result']:
        for host in result['data']['info']:
            result_list.append({
                'ip': host['host']['bk_host_innerip'],
                'os_name': host['host']['bk_os_name'],
                'host_name': host['host']['bk_host_name'],
                'bk_cloud_id': host['host']['bk_cloud_id'][0]['id'],
                'bk_cloud_name': host['host']['bk_cloud_id'][0]['bk_inst_name'],
                'bk_biz_id': host['biz'][0]['bk_biz_id'],
                'is_monitor': host['host']['bk_host_innerip'] in [item.ip for item in monitor_list]
            })

    return my_render_json(result_list)


@require_http_methods(["POST"])
def search_sys_data(request):
    client = get_client_by_request(request)
    param = json.loads(request.body)
    script_content = '''MEMORY=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
DISK=$(df -h | awk '$NF=="/"{printf "%s", $5}')
CPU=$(top -bn1 | grep load | awk '{printf "%.2f%%", $(NF-2)}')
DATE=$(date "+%Y-%m-%d %H:%M:%S")
echo -e "$DATE|$MEMORY|$DISK|$CPU"'''
    is_success, log_dict = execute_script_and_get_log(client, param['bk_biz_id'], param['ip_list'], script_content)
    if is_success:
        log_info = {}
        for log in log_dict.values():
            log_info = log

        metrics = log_info['log_content'].split('|')
        return my_render_json({
            'mem': metrics[1][:-1],
            'disk': metrics[2][:-1],
            'cpu': metrics[3][:-1],
        })

    else:
        return render_json({'reuslt': False, 'message': '查询失败'})


@require_http_methods(["POST"])
def add_monitor(request):
    param = json.loads(request.body)
    host = {
        'ip': param['ip'],
        'bk_cloud_id': param['bk_cloud_id'],
        'bk_biz_id': param['bk_biz_id'],
    }
    try:
        MonitorHost.objects.get(is_deleted=False, **host)
    except MonitorHost.DoesNotExist:
        host.update({
            'create_user': request.user.username,
            'update_user': request.user.username
        })
        MonitorHost.objects.create(**host)

    return my_render_json()


@require_http_methods(["POST"])
def remove_monitor(request):
    param = json.loads(request.body)
    host = {
        'ip': param['ip'],
        'bk_cloud_id': param['bk_cloud_id'],
        'bk_biz_id': param['bk_biz_id'],
    }
    try:
        instance = MonitorHost.objects.get(**host)
    except MonitorHost.DoesNotExist:
        pass
    else:
        instance.is_deleted = True
        instance.save()

    return my_render_json()


@require_http_methods(["GET"])
def render_chart(request):
    param = request.GET
    try:
        instance = MonitorHost.objects.get(id=param['id'])
    except (MonitorHost.DoesNotExist, MonitorHost.MultipleObjectsReturned) as e:
        return render_json({'result': False, 'message': '该主机数据异常'})

    t = datetime.datetime.now() + datetime.timedelta(hours=-1)
    data_list = HostData.objects.filter(host=instance, create_time__gte=t)
    xAxis = []
    cpu_series = {
        'name': 'cpu',
        'type': 'line',
        'data': []
    }
    mem_series = {
        'name': 'mem',
        'type': 'line',
        'data': []
    }
    disk_series = {
        'name': 'disk',
        'type': 'line',
        'data': []
    }
    for data in data_list:
        xAxis.append(str(data.create_time))
        cpu_series['data'].append(float(data.cpu))
        mem_series['data'].append(float(data.mem))
        disk_series['data'].append(float(data.disk))

    return my_render_json({'xAxis': xAxis, 'series': [cpu_series, mem_series, disk_series]})


@require_http_methods(["GET"])
def list_host(request):
    # param = request.GET
    result_list = []
    for item in MonitorHost.objects.all():
        result_list.append(model_to_dict(item))

    return my_render_json(result_list)
