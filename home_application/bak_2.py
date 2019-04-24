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
# from home_application.celery_tasks import monitor_task
from home_application.celery_tasks import get_job_log
from home_application.commons import CcApiAdapter, JobApiAdapter, get_job_log_content
# from home_application.models import JobRecord

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
    return render_mako_context(request, '/home_application/home.html')


def history(request):
    """
    首页
    """
    return render_mako_context(request, '/home_application/history.html')


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
    get_job_log()
    return render_json({'username': request.user.username, 'result': 'OK'})


@require_http_methods(["POST"])
def search_biz(request):
    client = get_client_by_request(request)
    param = json.loads(request.body)
    result = CcApiAdapter.search_business(client, **param)
    return render_json(result)


@require_http_methods(["POST"])
def search_set(request):
    client = get_client_by_request(request)
    param = json.loads(request.body)
    result = CcApiAdapter.search_set(client, **param)
    return render_json(result)


@require_http_methods(["POST"])
def search_host(request):
    client = get_client_by_request(request)
    param = json.loads(request.body)
    result = CcApiAdapter.search_host(client, **param)
    return render_json(result)


@require_http_methods(["POST"])
def execute_job(request):
    # 存记录到表里
    # 执行job
    client = get_client_by_request(request)
    param = json.loads(request.body)
    hosts = param.pop('hosts')
    ip_list = [{'ip': h['bk_host_innerip'], 'bk_cloud_id': h['bk_cloud_id']} for h in hosts]
    param['ip_list'] = ip_list
    execute_job_result = JobApiAdapter.execute_job(client, **param)
    if not execute_job_result['result']:
        return render_json({'result': False, 'message': execute_job_result['message']})

    job_record = {
        'bk_biz_id': param['bk_biz_id'],
        'job_id': param['bk_job_id'],
        'job_instance_id': execute_job_result['data']['job_instance_id'],
        'ips': ','.join([h['ip'] for h in ip_list]),
        'create_user': request.user.username,
        'update_user': request.user.username,
    }
    JobRecord.objects.create(**job_record)

    return my_render_json()


@require_http_methods(["GET"])
def search_record(request):
    param = request.GET
    record_list = JobRecord.objects.filter(bk_biz_id=param['bk_biz_id'])
    if param.get('ip'):
        record_list = record_list.filter(ips__contains=param['ip'])

    result_list = []
    for item in record_list:
        item_dict = model_to_dict(item)
        item_dict['status'] = item.get_status_display()
        item_dict['create_time'] = str(item.create_time)
        if item.log_content:
            item_dict['log_content'] = json.loads(item.log_content)
        else:
            item_dict['log_content'] = ''

        result_list.append(item_dict)

    return my_render_json(result_list)
