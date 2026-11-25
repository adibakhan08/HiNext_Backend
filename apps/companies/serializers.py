
from rest_framework import serializers

from .models import Company, CompanyContact


class CompanyContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanyContact
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class CompanySerializer(serializers.ModelSerializer):

    contacts = CompanyContactSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]
