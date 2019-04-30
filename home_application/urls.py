# -*- coding: utf-8 -*-

from django.conf.urls import patterns
from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'chinese', views.ChineseViewSet)
router.register(r'math', views.MathViewSet)

# 使用自动URL路由连接我们的API。
# 另外，我们还包括支持浏览器浏览API的登录URL。
urlpatterns = patterns(
    'home_application.views',
    (r'^$', 'home')
)

urlpatterns += [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
