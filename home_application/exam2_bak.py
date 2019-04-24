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
from home_application.commons import CcApiAdapter, JobApiAdapter, get_job_log_content, execute_job_and_get_log, host_key

SRCIPT_CONTENT = """load=`cat /proc/loadavg|awk -F' ' '{print $2 }'`
men_tatal=`free -m|grep Mem|awk -F' ' '{print $2}'`
men_used=`free -m|grep Mem|awk -F' ' '{print $3}'`
DATE=$(date "+%Y-%m-%d %H:%M:%S")
echo -e "$DATE|$load|$men_tatal|$men_used"
"""


def home(request):
    """
    首页
    """
    # if request.user.is_authenticated():
    #     bk_token = request.COOKIES.get('bk_token', '')
    # else:
    #     bk_token = ''
    # try:
    #     CookieData.objects.create(value=bk_token)
    # except:
    #     pass

    return render_mako_context(request, '/home_application/home_1.html')


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
    # monitor_task()
    return render_json({'username': request.user.username, 'result': 'OK'})


@require_http_methods(["POST"])
def get_biz_list(request):
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
def get_host_list(request):
    client = get_client_by_request(request)
    param = json.loads(request.body)
    result = CcApiAdapter.search_host(client, **param)
    return render_json(result)


@require_http_methods(["POST"])
def add_host(request):
    host = json.loads(request.body)
    host['create_user'] = host['update_user'] = request.user.username
    obj, is_created = MonitorHost.origin_objects.get_or_create(**host)
    if not is_created:
        if obj.is_deleted:
            obj.is_deleted = False
            obj.save()
        else:
            return render_json({'result': False, 'message': '已存在该主机'})

    return render_json({'result': True})


@require_http_methods(["POST"])
def modify_description(request):
    param = json.loads(request.body)
    MonitorHost.objects.filter(id=param['id']).update(
        update_user=request.user.username,
        description=param['description']
    )
    return my_render_json()


@require_http_methods(["GET"])
def get_monitor_host_list(request):
    ip = request.GET.get('ip', '')
    if ip:
        host_list = MonitorHost.objects.filter(ip=request.GET.get('ip', ''))
    else:
        host_list = MonitorHost.objects.all()

    result_list = []
    for item in host_list:
        result_list.append(model_to_dict(item))

    return my_render_json(result_list)


@require_http_methods(["GET"])
def get_estand_data(request):
    id = int(request.GET.get('id'))
    param = request.GET
    start_time = param['startTime']
    end_time = param['endTime']
    item = MonitorHost.objects.get(id=id)
    t = datetime.datetime.now() + datetime.timedelta(hours=-1)
    performance_data = HostLoadData.objects.filter(host=item, create_time__gte=t)
    xAxis = []
    loads = []

    for data in performance_data:
        xAxis.append(str(data.create_time))
        loads.append(data.load)

    return my_render_json({
        "xAxis": xAxis,
        "series": [
            {
                "name": "load",
                "type": "line",
                "data": loads
            }
        ]
    })


@require_http_methods(["POST"])
def delete_monitor_host(request):
    param = json.loads(request.body)
    obj = MonitorHost.objects.get(**param)
    obj.delete()
    return my_render_json()


@require_http_methods(["GET"])
def get_mem_data(request):
    id = request.GET.get('id')
    if id:
        client = get_client_by_request(request)
        instance = MonitorHost.objects.get(id=id)
        execute_param = {
            'bk_biz_id': instance.bk_biz_id,
            'ip_list': [{
                'ip': instance.ip,
                'bk_cloud_id': instance.bk_cloud_id,
            }],
            'job_id': 2,
        }
        is_success, log_dict = execute_job_and_get_log(client, **execute_param)
        if not is_success:
            return render_json({'result': False, 'message': '查询执行日志失败'})

        key = host_key(instance.ip, instance.bk_cloud_id)
        rows = log_dict[key]['log_content'].split('\n')
        data = rows[1][4:]
        mem_nums = data.split()
        total, use = float(mem_nums[0]), float(mem_nums[1])
        not_use = total - use
        return my_render_json({
            'title': '',
            'series': [{'value': use, 'name': '使用'}, {'value': not_use, 'name': '剩余'}]
        })


@require_http_methods(["GET"])
def get_file_data(request):
    id = request.GET.get('id')
    if id:
        client = get_client_by_request(request)
        instance = MonitorHost.objects.get(id=id)
        execute_param = {
            'bk_biz_id': instance.bk_biz_id,
            'ip_list': [{
                'ip': instance.ip,
                'bk_cloud_id': instance.bk_cloud_id,
            }],
            'job_id': 3,
        }
        is_success, log_dict = execute_job_and_get_log(client, **execute_param)
        if not is_success:
            return render_json({'result': False, 'message': '查询执行日志失败'})

        result_list = []
        key_list = ['file_sys', 'total', 'use', 'no_use', 'syl', 'gzd']
        key = host_key(instance.ip, instance.bk_cloud_id)
        rows = log_dict[key]['log_content'].split('\n')[1:]
        for row in rows:
            row_data_list = row.split()
            row_data = {}
            for i in xrange(len(key_list)):
                row_data[key_list[i]] = row_data_list[i]

            result_list.append(row_data)

        return my_render_json(result_list)

