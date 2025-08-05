#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit.settings')
django.setup()

from core.models import Customer, Loan

def show_sample_customers():
    """Show first 10 customers for testing"""
    print("Sample customers for testing:")
    print("-" * 50)
    
    customers = Customer.objects.all()[:10]
    for customer in customers:
        loan_count = Loan.objects.filter(customer=customer).count()
        print(f"ID: {customer.pk} | {customer.first_name} {customer.last_name} | Phone: {customer.phone_number} | Loans: {loan_count}")
    
    print("-" * 50)
    print(f"Total customers: {Customer.objects.count()}")
    print(f"Total loans: {Loan.objects.count()}")

if __name__ == "__main__":
    show_sample_customers()
