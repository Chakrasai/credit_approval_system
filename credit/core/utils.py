from datetime import date

def calculate_emi(principal, annual_rate, tenure_months):
    if principal <= 0 or annual_rate < 0 or tenure_months <= 0:
        raise ValueError("Invalid input values.")

    if annual_rate == 0:
        return round(principal / tenure_months, 2)

    try:
        monthly_rate = (annual_rate / 12) / 100
        emi = (principal * monthly_rate * (1 + monthly_rate) ** tenure_months) / \
              ((1 + monthly_rate) ** tenure_months - 1)
        return round(emi, 2)
    except OverflowError:
        raise ValueError("Interest rate or tenure too large.")

def calculate_credit_score(customer):
    loans = customer.loans.all()
    total_loan_outstanding = sum(loan.loan_amount for loan in loans)
    if total_loan_outstanding>customer.approved_limit:
        return 0
    if not loans.exists():
        return 100
    
    score = 0

    total_emi_paid = sum([loan.emis_paid_on_time for loan in loans])
    total_emi_expected = sum([loan.tenure for loan in loans])
    emi_score = (total_emi_paid / total_emi_expected * 100) if total_emi_expected > 0 else 0
    score += emi_score

    loan_count = loans.count()
    loan_count_score = min(loan_count * 4, 100)
    score += loan_count_score

    current_year = date.today().year
    current_year_loans = loans.filter(approval_date__year=current_year).count()
    score += min(current_year_loans * 10, 20)

    total_volume = sum([loan.loan_amount for loan in loans])
    volume_score = min(total_volume / 100000, 20)
    score += volume_score

    return round(score)
