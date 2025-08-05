from django.urls import path
from . import views
from .views import register_customer_view, CheckEligibilityView, CreateLoanView , ViewLoanBy_ID , ViewLoansBY_CustomerID

urlpatterns = [
    path('', views.home, name='home'),    
    path('register/', register_customer_view.as_view(), name='register_customer'),
    path('check-eligibility/', CheckEligibilityView.as_view(), name='check_eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='create_loan'),
    path('view-loan/<int:loan_id>/', ViewLoanBy_ID.as_view(), name='view_loan'),
    path('view-loan-customer/<int:customer_id>/', ViewLoansBY_CustomerID.as_view(), name='view_loan_customerID')
]