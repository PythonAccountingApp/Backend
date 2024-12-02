from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass  # 可在此處擴充 User 欄位


class Category(models.Model):
    CATEGORY_TYPE_CHOICES = [
        ("income", "Income"),
        ("expense", "Expense"),
    ]
    name = models.CharField(max_length=255)
    category_type = models.CharField(max_length=7, choices=CATEGORY_TYPE_CHOICES)

    def __str__(self):
        return f"{self.name} - {self.category_type}"


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("income", "Income"),
        ("expense", "Expense"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    discount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    description = models.CharField(max_length=255, blank=True)
    store = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField(default=timezone.localdate)
    time = models.TimeField(default=timezone.localtime)
    detail = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.description} - {self.amount} on {self.date}"
