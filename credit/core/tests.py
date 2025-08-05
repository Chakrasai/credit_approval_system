from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Customer, Loan
from .utils import calculate_emi
from datetime import date
from dateutil.relativedelta import relativedelta

class CreditAPITestCase(TestCase):
    """
    TestCase for Credit API endpoints.
    This test suite covers the following functionalities:
    - Customer Registration:
        - `test_register_customer`: Tests the registration endpoint for creating a new customer and verifies the response data.
    - Loan Eligibility Check:
        - `test_check_eligibility_approved`: Tests the loan eligibility endpoint to ensure it returns the correct approval status for a valid customer and loan request.
    - Loan Creation:
        - `test_create_loan_success`: Tests the loan creation endpoint for a successful loan application, verifying approval and loan ID in the response.
    - Loan Retrieval:
        - `test_view_loan_by_id`: Tests retrieval of a specific loan by its ID, ensuring the correct loan details are returned.
        - `test_view_loans_by_customer`: Tests retrieval of all loans associated with a specific customer, verifying that at least one loan is returned.
    Setup:
        - Creates a test customer for use in the test cases.
    Dependencies:
        - Assumes existence of Customer and Loan models, and utility function `calculate_emi`.
        - Uses Django REST Framework's APIClient for API requests.
    """
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=30,
            phone_number="1234567890",
            monthly_salary=60000,
            approved_limit=300000
        )

    def test_register_customer(self):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "age": 32,
            "phone_number": "9876543210",
            "monthly_salary": 50000,
            "approved_limit": 250000
        }
        response = self.client.post("/api/register/", data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['first_name'], "John")

    def test_check_eligibility_approved(self):
        data = {
            "customer_id": self.customer.pk,
            "loan_amount": 50000,
            "interest_rate": 15.0,
            "tenure": 12
        }
        response = self.client.post("/api/check-eligibility/", data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("loan_approved", response.json())

    def test_create_loan_success(self):
        payload = {
            "customer_id": self.customer.pk,
            "loan_amount": 80000,
            "interest_rate": 14,
            "tenure": 12
        }
        response = self.client.post("/api/create-loan/", data=payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["loan_approved"])
        self.assertIn("loan_id", response.json())

    def test_view_loan_by_id(self):
        loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=70000,
            interest_rate=14,
            tenure=12,
            monthly_installment=calculate_emi(70000, 14, 12),
            emis_paid_on_time=0,
            approval_date=date.today(),
            end_date=date.today() + relativedelta(months=12)
        )
        response = self.client.get(f"/api/view-loan/{loan.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["loan_id"], loan.pk)

    def test_view_loans_by_customer(self):
        Loan.objects.create(
            customer=self.customer,
            loan_amount=100000,
            interest_rate=13.5,
            tenure=24,
            monthly_installment=calculate_emi(100000, 13.5, 24),
            emis_paid_on_time=0,
            approval_date=date.today(),
            end_date=date.today() + relativedelta(months=24)
        )
        response = self.client.get(f"/api/view-loan-customer/{self.customer.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)
