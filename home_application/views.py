# -*- coding: utf-8 -*-
import datetime
import json
import time

import requests
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from account.decorators import login_exempt
from blueking.component.shortcuts import get_client_by_request
from common.mymako import render_mako_context, my_render_json
from common.mymako import render_json
from conf.default import APP_ID, APP_TOKEN, BK_PAAS_HOST
from home_application.celery_tasks import chain_task
from home_application.commons import CcApiAdapter, JobApiAdapter, get_job_log_content, execute_job_and_get_log, \
    host_key, execute_script_and_get_log
from .models import TestInfo
from django.shortcuts import render

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
    # param1 = {
    #     'a': '1'
    # }
    # param2 = {
    #     'b': '2'
    # }
    # chain_task.delay(param1, param2)
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
    return render_json({'username': request.user.username, 'result': 'OK'})

def get_data(request):
    """
    获取全部学生信息
    """
    data = TestInfo.objects.all()#查询集
    list_data = []
    result_data = list(data)      #实例列表
    for i in result_data:
        xx = {}
        xx['id'] = i.id
        xx['name'] = i.name
        xx['gender'] = i.gender
        xx['age'] = i.age
        xx['score'] = i.score
        list_data.append(xx)
    return HttpResponse(json.dumps(list_data))
    # return render(request,'home.html',data)

def get_partInfo(request):
    """
    获取部分学生信息
    """
    param = request.GET['name']
    data = TestInfo.objects.all()     #查询集
    list_data = []
    result_data = list(data)      #实例列表
    for i in result_data:
        if param in i.name:
            xx = {}
            xx['id'] = i.id
            xx['name'] = i.name
            xx['gender'] = i.gender
            xx['age'] = i.age
            xx['score'] = i.score
            list_data.append(xx)
    return HttpResponse(json.dumps(list_data))

def add_data(request):
    """
    新增信息到数据库
    """
    param = request.body
    datas = json.loads(param)
    params = datas['form']
    TestInfo.objects.create(**params)
    list_data = {'is_ok': True}
    return HttpResponse(json.dumps(list_data))

def update_data(request):
    """
    更新数据库数据
    """
    param = request.body
    datas = json.loads(param)
    params = datas['form1']
    input_id = params.pop('id')
    TestInfo.objects.filter(id=input_id).update(**params)
    list_data = {'is_ok': True}
    return HttpResponse(json.dumps(list_data))

def delete_data(request):
    """
    删除数据库数据
    """
    param = request.body
    datas = json.loads(param)
    input_id = datas['id']
    TestInfo.objects.filter(id=input_id).delete()
    list_data = {'is_ok': True}
    return HttpResponse(json.dumps(list_data))