# -*- coding: utf-8 -*-
from django.db import models


class OperateManager(models.Manager):
    def all(self, *args, **kwargs):
        return super(OperateManager, self).filter(is_deleted=False)

    def filter(self, *args, **kwargs):
        return super(OperateManager, self) \
            .filter(*args, **kwargs).filter(is_deleted=False)


class OperateRecordModel(models.Model):
    objects = OperateManager()
    origin_objects = models.Manager()

    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    create_user = models.CharField(u"创建人", max_length=32, blank=True)
    update_time = models.DateTimeField(u"修改时间", auto_now=True)
    update_user = models.CharField(u"修改人", max_length=32, blank=True)
    is_deleted = models.BooleanField(u"是否删除", default=False)

    def delete(self):
        self.is_deleted = True
        self.save()

    class Meta:
        abstract = True


# class MonitorHost(OperateRecordModel):
#     ip = models.CharField(max_length=15)
#     bk_cloud_id = models.IntegerField()
#     bk_biz_id = models.IntegerField()
#
#
# class HostData(OperateRecordModel):
#     mem = models.FloatField()
#     disk = models.FloatField()
#     cpu = models.FloatField()
#     host = models.ForeignKey(MonitorHost, related_name="data")

# class MonitorItem(OperateRecordModel):
#     ip = models.CharField(max_length=15)
#     bk_cloud_id = models.IntegerField()
#     bk_biz_id = models.IntegerField()
#
#
# class MonitorData(OperateRecordModel):
#     mem = models.FloatField()
#     disk = models.FloatField()
#     cpu = models.FloatField()
#     monitor_item = models.ForeignKey(MonitorItem, related_name="data")

# class MonitorHost(OperateRecordModel):
#     ip = models.CharField(max_length=15)
#     host_name = models.CharField(max_length=50)
#     bk_biz_id = models.IntegerField()
#     bk_biz_name = models.CharField(max_length=50)
#     bk_cloud_name = models.CharField(max_length=50)
#     os_name = models.CharField(max_length=50)
#     bk_cloud_id = models.IntegerField(default=0)
#     description = models.TextField(null=True, blank=True)
#
#
# class HostLoadData(OperateRecordModel):
#     host = models.ForeignKey(MonitorHost, related_name='data')
#     load = models.FloatField()
#     local_time = models.DateTimeField(null=True)
#
#
# class CookieData(OperateRecordModel):
#     value = models.CharField(max_length=200)

class TestInfo(models.Model):
    name = models.CharField(max_length=10)
    gender = models.CharField(max_length=5)
    age = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

class ChineseScore(models.Model):
    name = models.CharField(max_length=10)
    gender = models.CharField(max_length=5)
    age = models.IntegerField(default=0)
    chinese_score = models.IntegerField(default=0)

class MathScores(models.Model):
    name = models.CharField(max_length=10)
    gender = models.CharField(max_length=5)
    age = models.IntegerField(default=0)
    math_score = models.IntegerField(default=0)
    english_score = models.IntegerField(default=0)

