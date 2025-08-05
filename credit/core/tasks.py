import pandas as pd
from celery import shared_task
from .models import Customer, Loan
from datetime import datetime
from decouple import config
@shared_task
def ingest_customer_data():
    df = pd.read_excel(config('CUSTOMER_DATA_PATH'), engine='openpyxl')
    print("customer started")
    for _,row in df.iterrows():
        Customer.objects.update_or_create(
            phone_number = row['Phone Number'],
            defaults={
                "id": row['Customer ID'],
                "first_name": row['First Name'],
                "last_name": row['Last Name'],
                "monthly_salary": row['Monthly Salary'],
                "approved_limit": row['Approved Limit'],
                "age": row['Age']
            }
        )

@shared_task
def ingest_loan_data():
    df = pd.read_excel(config('LOAN_DATA_PATH'), engine='openpyxl')
    print("loan started")
    for _,row in df.iterrows():
        customer = Customer.objects.get(id=row['Customer ID'])
        Loan.objects.update_or_create(
            id = row['Loan ID'],
            defaults={
                "customer": customer,
                "loan_amount": row['Loan Amount'],
                "tenure": row['Tenure'],
                "interest_rate": row['Interest Rate'],
                "monthly_installment": row['Monthly payment'],
                "emis_paid_on_time": row['EMIs paid on Time'],
                "approval_date": pd.to_datetime(row['Date of Approval']).date(),
                "end_date": pd.to_datetime(row['End Date']).date(),
            }
        )

