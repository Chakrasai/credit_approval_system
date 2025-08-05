#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit.settings')
django.setup()

from core.tasks import ingest_customer_data, ingest_loan_data

def test_celery_tasks():
    print("Testing Celery tasks...")
    
    # Test customer data ingestion
    try:
        print("Testing customer data ingestion...")
        result = ingest_customer_data.delay()
        print(f"Customer data task result: {result}")
        print("Customer data ingestion task submitted successfully!")
    except Exception as e:
        print(f"Error in customer data ingestion: {e}")
    
    # Test loan data ingestion
    try:
        print("Testing loan data ingestion...")
        result = ingest_loan_data.delay()
        print(f"Loan data task result: {result}")
        print("Loan data ingestion task submitted successfully!")
    except Exception as e:
        print(f"Error in loan data ingestion: {e}")

if __name__ == "__main__":
    test_celery_tasks()
