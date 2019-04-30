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
from .models import ChineseScore,MathScores
from rest_framework import viewsets
from .serializers import ChineseSerializer,MathSerializer
import django_filters
from django_filters import STRICTNESS
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.shortcuts import render


def home(request):
    """
    首页
    """
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


# drf模式

class ChineseFtr(django_filters.FilterSet):
    class Meta:
        model = ChineseScore
        strict = STRICTNESS.RAISE_VALIDATION_ERROR
        fields = ("id", "name")

class ChineseViewSet(viewsets.ModelViewSet):
    queryset = ChineseScore.objects.all()
    serializer_class = ChineseSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = ChineseFtr

class MathFtr(django_filters.FilterSet):
    class Meta:
        model = MathScores
        strict = STRICTNESS.RAISE_VALIDATION_ERROR
        fields = ("id", "name")

class MathViewSet(viewsets.ModelViewSet):
    queryset = MathScores.objects.all()
    serializer_class = MathSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = MathFtr









