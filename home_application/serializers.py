from .models import ChineseScore,MathScores
from rest_framework import serializers


class ChineseSerializer(serializers.ModelSerializer):
    # age = serializers.IntegerField()
    # name = serializers.CharField(max_length=12)
    # chinese_score = serializers.CharField(required=False)

    class Meta:
        model = ChineseScore
        fields = ('id', 'name', 'gender', 'age','chinese_score')


class MathSerializer(serializers.ModelSerializer):
    class Meta:
        model = MathScores
        fields = ('id', 'name', 'gender', 'age','math_score','english_score')
