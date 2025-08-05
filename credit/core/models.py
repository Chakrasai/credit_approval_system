from django.db import models
from pandas import unique

# Create your models here.

class Customer(models.Model):
    # id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    age = models.PositiveIntegerField()
    phone_number = models.CharField(max_length=15, unique=True)
    monthly_salary = models.IntegerField()
    approved_limit = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Loan(models.Model):
    # id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    monthly_installment = models.FloatField()
    emis_paid_on_time = models.IntegerField()
    approval_date = models.DateField()
    end_date = models.DateField()

    def __str__(self) -> str:
        return f"Loan {self.pk} for {self.customer.first_name} {self.customer.last_name}"