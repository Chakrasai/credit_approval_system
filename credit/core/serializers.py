from wsgiref import validate
from rest_framework import serializers
from .models import Customer, Loan

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age','phone_number', 'monthly_salary']

    def create(self, validated_data):
        income = validated_data.pop('monthly_salary')
        approval_limit = round((income *36)/100000) * 100000

        customer = Customer.objects.create(
            approved_limit = approval_limit,
            monthly_salary = income,
            **validated_data
        )

        return customer
    def to_representation(self, instance):
        return {
            "id":instance.id,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "age": instance.age,
            "phone_number": instance.phone_number,
            "monthly_salary": instance.monthly_salary,
            "approved_limit": instance.approved_limit
        }
        
