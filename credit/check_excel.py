#!/usr/bin/env python
import pandas as pd

def check_excel_files():
    print("Checking customer_data.xlsx columns:")
    try:
        df_customer = pd.read_excel(r'C:\Users\chakr\OneDrive\Desktop\django_pro\credit\media\customer_data.xlsx')
        print("Customer data columns:", df_customer.columns.tolist())
        print("Customer data shape:", df_customer.shape)
        print("First few rows:")
        print(df_customer.head())
    except Exception as e:
        print(f"Error reading customer data: {e}")
    
    print("\n" + "="*50 + "\n")
    
    print("Checking loan_data.xlsx columns:")
    try:
        df_loan = pd.read_excel(r'C:\Users\chakr\OneDrive\Desktop\django_pro\credit\media\loan_data.xlsx')
        print("Loan data columns:", df_loan.columns.tolist())
        print("Loan data shape:", df_loan.shape)
        print("First few rows:")
        print(df_loan.head())
    except Exception as e:
        print(f"Error reading loan data: {e}")

if __name__ == "__main__":
    check_excel_files()
