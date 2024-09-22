from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MinValueValidator
from django.db.models import CASCADE, Sum

# Choices
roles = [('admin', 'Admin'), ('user', 'User')]
frequency = [('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')]
investment_term = [('year', 12), ('two_years', 24), ('three_years', 36)]


# User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, firstname, lastname, password=None):
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            first_name=firstname,
            last_name=lastname,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, firstname, lastname, password=None):
        user = self.create_user(email, firstname, lastname, password)
        user.is_admin = True
        user.is_active = True  # Superuser should be active
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=20, choices=roles, default='user')
    is_active = models.BooleanField(default=False)
    two_fa = models.BooleanField(default=False, null=True)
    last_login = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


class FinancialStatus(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE, db_index=True)
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    net_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_savings = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_monthly_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                                 validators=[MinValueValidator(0)])
    total_investments = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                            validators=[MinValueValidator(0)])
    total_financial_goal = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                               validators=[MinValueValidator(0)])
    total_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_net_earnings(self):
        self.net_earnings = self.incomesource_set.aggregate(total=Sum('income_amount'))['total'] or 0
        self.save()

    def update_debt_amount(self):
        self.total_debt = self.debtamount_set.aggregate(total=Sum('debt_amount'))['total'] or 0
        self.save()

    def update_total_monthly_expenses(self):
        self.total_monthly_expenses = self.totalmonthlyexpenses_set.aggregate(total=Sum('estimated_expenses_cost'))[
                                          'total'] or 0
        self.save()

    def update_savings_total(self):
        self.total_savings = self.savings_set.aggregate(total=Sum('actual_amount'))['total'] or 0
        self.save()

    def update_financialgoal_total(self):
        self.total_financial_goal = self.financialgoals_set.aggregate(total=Sum('target_amount'))['total'] or 0
        self.save()


class IncomeSource(models.Model):
    financial_status = models.ForeignKey(FinancialStatus, on_delete=CASCADE, db_index=True)
    income_source = models.CharField(max_length=100, blank=True)
    income_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    frequency = models.CharField(max_length=10, choices=frequency, default='monthly')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.financial_status.update_net_earnings()


class DebtAmount(models.Model):
    financial_status = models.ForeignKey(FinancialStatus, on_delete=CASCADE, db_index=True)
    debt_name = models.CharField(max_length=500, blank=True)
    debt_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], blank=True)
    debt_frequency = models.CharField(max_length=10, choices=frequency, blank=True)
    debt_due_date = models.DateField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.financial_status.update_debt_amount()


class TotalMonthlyExpenses(models.Model):
    financial_status = models.ForeignKey(FinancialStatus, on_delete=CASCADE, db_index=True)
    expense_name = models.CharField(max_length=500, blank=True)
    estimated_expenses_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                                  validators=[MinValueValidator(0)])
    actual_expenses_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                               validators=[MinValueValidator(0)])
    frequency = models.CharField(max_length=10, choices=frequency, default='monthly')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.financial_status.update_total_monthly_expenses()


class Savings(models.Model):
    financial_status = models.ForeignKey(FinancialStatus, on_delete=CASCADE, db_index=True)
    savings_plan_title = models.CharField(max_length=500, blank=True)
    planned_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    actual_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    frequency = models.CharField(max_length=10, choices=frequency, default='monthly')
    savings_term = models.DateField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.financial_status.update_savings_total()


class FinancialGoals(models.Model):
    financial_status = models.ForeignKey(FinancialStatus, on_delete=CASCADE, db_index=True)
    goal_title = models.CharField(max_length=500, blank=True)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    goal_deadline = models.DateField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.financial_status.update_financialgoal_total()


class Investments(models.Model):
    financial_status = models.ForeignKey(FinancialStatus, on_delete=CASCADE, db_index=True)
    investment_type = models.CharField(max_length=500, choices=investment_term, blank=False)
    amount_invested = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    currently_invested = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                             validators=[MinValueValidator(0)])
    return_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.financial_status.update_investment_total()


class FinancialTips(models.Model):
    advice_title = models.CharField(max_length=500, blank=False)
    advice_content = models.TextField(max_length=10000)
    category = models.CharField(max_length=500, choices=[('Investment', 'Investment'), ('Savings', 'Savings'),
                                                         ('Debt_reduction', 'Debt Reduction'), ('Credit', 'Credit')],
                                blank=False)
