import re

from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from rest_framework import serializers

from .constants import PHONE_NUMBER_LENGTH
from .models import User, Contact, SpamReport

phone_number_matching_ptrn = re.compile(rf'^\d{{{PHONE_NUMBER_LENGTH}}}$')
class CustomUserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'phone_number', 'name', 'password', 're_password')

    def validate(self, attrs):
        if attrs['password'] != attrs['re_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def validate_phone_number(self, value):
        if not phone_number_matching_ptrn.match(value):
            raise serializers.ValidationError("Phone number must be a 10-digit number.")
        return value

class CustomUserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ('id', 'phone_number', 'name', 'email')



class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'phone_number']

    def validate_phone_number(self, value):
        if not phone_number_matching_ptrn.match(value):
            raise serializers.ValidationError("Phone number must be a 10-digit number.")
        return value

class SpamReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpamReport
        fields = ['id', 'phone_number', 'reported_at']
        read_only_fields = ['reported_at']

    def validate(self, attrs):
        user = self.context['request'].user
        number = attrs['phone_number']

        if SpamReport.objects.filter(reporter=user, phone_number=number).exists():
            raise serializers.ValidationError("You've already reported this number as spam.")
        return attrs

    def validate_phone_number(self, value):
        if not phone_number_matching_ptrn.match(value):
            raise serializers.ValidationError("Phone number must be a 10-digit number.")
        return value