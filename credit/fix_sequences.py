#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit.settings')
django.setup()

from django.db import connection
from core.models import Customer, Loan

def fix_sequences():
    """Fix PostgreSQL sequences after bulk data import"""
    print("Fixing PostgreSQL sequences...")
    
    with connection.cursor() as cursor:
        # Get current max IDs
        max_customer_id = Customer.objects.aggregate(max_id=models.Max('id'))['max_id'] or 0
        max_loan_id = Loan.objects.aggregate(max_id=models.Max('id'))['max_id'] or 0
        
        print(f"Max Customer ID: {max_customer_id}")
        print(f"Max Loan ID: {max_loan_id}")
        
        # Fix Customer sequence
        cursor.execute(f"SELECT setval('core_customer_id_seq', {max_customer_id + 1});")
        print("Fixed Customer sequence")
        
        # Fix Loan sequence  
        cursor.execute(f"SELECT setval('core_loan_id_seq', {max_loan_id + 1});")
        print("Fixed Loan sequence")
        
    print("Sequences fixed successfully!")
    
    # Test by creating a new customer
    print("\nTesting sequence fix...")
    try:
        from core.serializers import CustomerSerializer
        test_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'age': 25,
            'phone_number': '9999999999',
            'monthly_salary': 50000
        }
        serializer = CustomerSerializer(data=test_data)
        if serializer.is_valid():
            customer = serializer.save()
            print(f"Successfully created test customer with ID: {customer.id}")
            customer.delete()  # Clean up
            print("Test customer deleted")
        else:
            print(f"Serializer errors: {serializer.errors}")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    from django.db import models
    fix_sequences()
