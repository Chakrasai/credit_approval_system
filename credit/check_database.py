#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit.settings')
django.setup()

from core.models import Customer, Loan

def check_database():
    print("Checking database contents...")
    
    customer_count = Customer.objects.count()
    loan_count = Loan.objects.count()
    
    print(f"Total customers: {customer_count}")
    print(f"Total loans: {loan_count}")
    
    if customer_count > 0:
        print("\nFirst 5 customers:")
        for customer in Customer.objects.all()[:5]:
            print(f"  {customer.pk}: {customer.first_name} {customer.last_name} - {customer.phone_number}")
    
    if loan_count > 0:
        print("\nFirst 5 loans:")
        for loan in Loan.objects.all()[:5]:
            print(f"  Loan {loan.pk}: {loan.customer.first_name} {loan.customer.last_name} - ${loan.loan_amount}")

if __name__ == "__main__":
    check_database()
