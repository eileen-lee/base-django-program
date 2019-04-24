# -*- coding: utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns(
    'home_application.views',
    (r'^$', 'home'),
    (r'^host_status/$', 'host_status'),
    (r'^test_drf/$', 'test_drf'),
    (r'^dev-guide/$', 'dev_guide'),
    (r'^api/test/$', 'test'),
    (r'^get_data/$', 'get_data'),
    (r'^get_partInfo/$', 'get_partInfo'),
    (r'^add_data/$', 'add_data'),
    (r'^update_data/$', 'update_data'),
    (r'^delete_data/$', 'delete_data'),
)
