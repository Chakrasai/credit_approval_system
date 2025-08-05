from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomerSerializer
from .models import Customer, Loan
import math
from datetime import datetime, timedelta
from .utils import calculate_credit_score, calculate_emi 
# Create your views here.

def home(request):
    return HttpResponse("Welcome to the Credit App Home Page!")

class register_customer_view(APIView):
    """
    API view for registering a new customer.

    POST:
        Expects customer data in the request body.
        Validates the data using CustomerSerializer.
        If valid, creates and returns the new customer data with HTTP 201 status.
        If invalid, returns validation errors with HTTP 400 status.
    """
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class CheckEligibilityView(APIView):
    """
    CheckEligibilityView(APIView)
    -----------------------------
    POST /check-eligibility/
    This API endpoint checks a customer's eligibility for a loan based on their credit score, salary, and requested loan parameters. It also applies business rules to approve, reject, or adjust the loan offer.
    Request Body:
        - customer_id (int, required): The unique identifier of the customer applying for the loan.
        - loan_amount (float, required): The amount of loan requested.
        - interest_rate (float, required): The interest rate requested for the loan.
        - tenure (int, required): The tenure (in months) for the loan.
    Process:
        1. Validates that all required fields are present in the request.
        2. Retrieves the customer by customer_id. Returns 404 if not found.
        3. Validates the format of loan_amount, interest_rate, and tenure.
        4. Calculates the customer's credit score.
        5. Computes the sum of existing EMIs for the customer.
        6. Calculates the EMI for the new loan request.
        7. If total EMIs (existing + new) exceed 50% of the customer's monthly salary, the loan is rejected.
        8. Applies approval rules based on credit score:
            - If credit score > 50: Loan is approved at requested interest rate.
            - If 30 < credit score <= 50: Loan is approved if interest_rate >= 12%, else interest rate is corrected to 12%.
            - If 10 < credit score <= 30: Loan is approved if interest_rate >= 16%, else interest rate is corrected to 16%.
            - If credit score <= 10: Loan is rejected.
        9. If approved, creates a new Loan record with the appropriate parameters and returns the loan_id.
        10. Returns a response with the approval status, message, and calculated monthly installment.
    Responses:
        - 200 OK: Returns loan approval status, message, loan_id (if approved), and monthly installment.
        - 400 Bad Request: Missing or invalid fields in the request.
        - 404 Not Found: Customer does not exist.
        - 500 Internal Server Error: Error occurred while creating the loan record.
    Response Example (Success):
        {
            "loan_id": 123,
            "customer_id": 1,
            "loan_approved": true,
            "message": "Loan approved",
            "monthly_installment": 2500.0
        }
    Response Example (Rejected):
        {
            "loan_id": null,
            "customer_id": 1,
            "loan_approved": false,
            "monthly_installment": 3000.0
        }
    """
    def post(self, request):
        try:
            customer_id = request.data.get('customer_id')
            loan_amount = request.data.get('loan_amount')
            interest_rate = request.data.get('interest_rate')
            tenure = request.data.get('tenure')
            
            # Check for missing required fields
            missing_fields = []
            if not customer_id:
                missing_fields.append('customer_id')
            if not loan_amount:
                missing_fields.append('loan_amount')
            if not interest_rate:
                missing_fields.append('interest_rate')
            if not tenure:
                missing_fields.append('tenure')
            
            if missing_fields:
                return Response({
                    "error": f"Missing required fields: {', '.join(missing_fields)}",
                    "received_data": dict(request.data) if hasattr(request.data, 'items') else str(request.data)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({
                "error": f"Customer with id {customer_id} does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({
                "error": "Invalid customer_id format"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            loan_amount = float(loan_amount)
            interest_rate = float(interest_rate)
            tenure = int(tenure)
        except (ValueError, TypeError):
            return Response({
                "error": "Invalid loan_amount, interest_rate, or tenure format"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        credit_score = calculate_credit_score(customer)
        
        # Calculate existing EMIs
        existing_loans = Loan.objects.filter(customer=customer)
        existing_emis = sum([
            calculate_emi(loan.interest_rate, loan.loan_amount, loan.tenure)
            for loan in existing_loans
        ])
        
        new_emi = calculate_emi(interest_rate, loan_amount, tenure)

        # Hard reject if EMIs exceed 50% of salary
        if (existing_emis + new_emi) > (0.5 * customer.monthly_salary):
            return Response({
                "loan_id": None,
                "customer_id": customer.pk,
                "loan_approved": False,
                "message": "Loan not approved: EMI exceeds 50% of monthly salary",
                "monthly_installment": new_emi
            }, status=status.HTTP_200_OK)

        # Apply approval rules
        loan_approved = False
        corrected_interest_rate = interest_rate
        message = ""
        loan_id = None

        if credit_score > 50:
            loan_approved = True
            message = "Loan approved"
        elif 30 < credit_score <= 50:
            if interest_rate >= 12:
                loan_approved = True
                message = "Loan approved"
            else:
                corrected_interest_rate = 12
                new_emi = calculate_emi(corrected_interest_rate, loan_amount, tenure)
                loan_approved = True
                message = f"Loan approved with corrected interest rate: {corrected_interest_rate}%"
        elif 10 < credit_score <= 30:
            if interest_rate >= 16:
                loan_approved = True
                message = "Loan approved"
            else:
                corrected_interest_rate = 16
                new_emi = calculate_emi(corrected_interest_rate, loan_amount, tenure)
                loan_approved = True
                message = f"Loan approved with corrected interest rate: {corrected_interest_rate}%"
        else:
            loan_approved = False
            message = f"Loan not approved: Credit score too low ({credit_score})"

        # If loan is approved, create the loan record and get loan_id
        if loan_approved:
            try:
                final_interest_rate = corrected_interest_rate if corrected_interest_rate != interest_rate else interest_rate
                final_emi = calculate_emi(final_interest_rate, loan_amount, tenure)
                
                # We need to set approval_date and end_date for the loan
                from datetime import date, timedelta
                from dateutil.relativedelta import relativedelta
                
                approval_date = date.today()
                end_date = approval_date + relativedelta(months=tenure)
                
                loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=loan_amount,
                    interest_rate=final_interest_rate,
                    tenure=tenure,
                    monthly_installment=final_emi,
                    emis_paid_on_time=0,  # Start with 0
                    approval_date=approval_date,
                    end_date=end_date
                )
                loan_id = loan.pk
                new_emi = final_emi
            except Exception as e:
                return Response({
                    "loan_id": None,
                    "customer_id": customer.pk,
                    "loan_approved": False,
                    "message": f"Error creating loan: {str(e)}",
                    "monthly_installment": new_emi
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "loan_id": loan_id,
            "customer_id": customer.pk,
            "loan_approved": loan_approved,
            "message": message,
            "monthly_installment": new_emi
        }, status=status.HTTP_200_OK)
    

class CreateLoanView(APIView):
    """
    APIView for creating a new loan for a customer.
    POST:
        Creates a loan for a customer based on their credit score, salary, and requested loan details.
        The loan approval process includes:
            - Validating the existence of the customer.
            - Calculating the customer's credit score.
            - Summing up existing EMIs and ensuring the new EMI does not exceed 50% of the customer's monthly salary.
            - Adjusting the interest rate and approval status based on the credit score:
                - Credit score > 50: Approve at requested interest rate.
                - 30 < Credit score <= 50: Approve if interest rate >= 12%, otherwise adjust to 12%.
                - 10 < Credit score <= 30: Approve if interest rate >= 16%, otherwise adjust to 16%.
                - Credit score <= 10: Reject or adjust interest rate to at least 20%.
            - Creating the loan if approved, or returning a rejection message.
    Request Data:
        - customer_id (int): ID of the customer applying for the loan.
        - loan_amount (float): Requested loan amount.
        - interest_rate (float): Requested interest rate.
        - tenure (int): Loan tenure in months.
    Responses:
        - 201 Created: Loan approved and created. Returns loan details.
        - 200 OK: Loan not approved. Returns reason and calculated EMI.
        - 400 Bad Request: Invalid data format.
        - 404 Not Found: Customer does not exist.
    Returns:
        JSON response with loan approval status, message, and EMI details.
    """
    def post(self, request):
        try:
            customer = Customer.objects.get(id=request.data['customer_id'])
        except Customer.DoesNotExist:
            return Response({
                "error": f"Customer with id {request.data['customer_id']} does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        
        loan_amount = float(request.data['loan_amount'])
        interest_rate = float(request.data['interest_rate'])
        tenure = int(request.data['tenure'])

        credit_score = calculate_credit_score(customer)

        try:
            existing_emis = sum([
                calculate_emi(loan.loan_amount, loan.interest_rate, loan.tenure)
                for loan in Loan.objects.filter(customer=customer)
            ])
            new_emi = calculate_emi(loan_amount, interest_rate, tenure)
        except ValueError as e:
            return Response({
                "error": f"Invalid data format: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if (existing_emis + new_emi) > (0.5 * customer.monthly_salary):
            return Response({
                "loan_id": None,
                "customer_id": customer.pk,
                "loan_approved": False,
                "message": "EMI exceeds 50% of monthly salary",
                "monthly_installment": new_emi
            }, status=200)
        
        approval = False
        corrected_interest_rate = interest_rate

        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            approval = interest_rate >= 12
            corrected_interest_rate = max(interest_rate, 12)
        elif 10 < credit_score <= 30:
            approval = interest_rate >= 16
            corrected_interest_rate = max(interest_rate, 16)
        else:
            approval = False
            corrected_interest_rate = max(interest_rate, 20)

        corrected_emi = calculate_emi(loan_amount, corrected_interest_rate, tenure)

        if approval:
            # Loan approved – create it
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                interest_rate=corrected_interest_rate,
                tenure=tenure,
                monthly_installment=corrected_emi,
                emis_paid_on_time=0,
                approval_date=datetime.today().date(),
                end_date=(datetime.today() + timedelta(days=30*tenure)).date()
            )

            return Response({
                "loan_id": loan.pk,
                "customer_id": customer.pk,
                "loan_approved": True,
                "message": "Loan approved",
                "monthly_installment": corrected_emi
            }, status=201)

        else:
            return Response({
                "loan_id": None,
                "customer_id": customer.pk,
                "loan_approved": False,
                "message": "Loan not approved due to low credit score",
                "monthly_installment": corrected_emi
            }, status=200)

class ViewLoanBy_ID(APIView):

    def get(self,request, loan_id):
        try:
            loan = Loan.objects.get(id=loan_id)
        except Loan.DoesNotExist:
            return Response({
                "error": "Loan not found"
            })
        
        customer = loan.customer

        return Response({
            "loan_id": loan_id,
            "customer": {
                "customer_id": customer.pk,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone_number": customer.phone_number,
                "age": customer.age
            },
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": calculate_emi(loan.loan_amount, loan.interest_rate, loan.tenure),
            "tenure": loan.tenure
        }, status=status.HTTP_200_OK)


class ViewLoansBY_CustomerID(APIView):
    """
    API view to retrieve all loans associated with a specific customer by their ID.
    GET:
        Retrieves a list of loans for the customer with the given customer_id.
        Each loan entry includes:
            - loan_id: Unique identifier of the loan.
            - loan_amount: The principal amount of the loan.
            - interest_rate: The interest rate applied to the loan.
            - monthly_installment: The calculated EMI (Equated Monthly Installment) for the loan.
            - repayments_left: Number of monthly repayments remaining until the loan end date.
    Path Parameters:
        customer_id (int): The unique identifier of the customer.
    Responses:
        200 OK:
            Returns a list of loans with their details for the specified customer.
        404 Not Found:
            Returned if the customer with the given ID does not exist.
    Raises:
        Customer.DoesNotExist: If no customer is found with the provided customer_id.
    """
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
        
        loans = Loan.objects.filter(customer=customer)

        loans_data = []
        for loan in loans:
            today = datetime.today()
            repayments_left = max(0,(loan.end_date.year-today.year)*12+(loan.end_date.month - today.month))

            loans_data.append({
                "loan_id": loan.pk,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": calculate_emi(loan.loan_amount, loan.interest_rate, loan.tenure),
                "repayments_left": repayments_left
            })

        return Response(loans_data,status=status.HTTP_200_OK)    


