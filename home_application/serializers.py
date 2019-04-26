from .models import TestInfo
from rest_framework import serializers

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestInfo
        fields = ('id', 'name', 'gender', 'age','score')
