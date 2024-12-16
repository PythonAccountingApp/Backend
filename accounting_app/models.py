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
    amount = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    discount = models.DecimalField(default=0, max_digits=20, decimal_places=2, blank=True)
    description = models.CharField(default="", max_length=255, blank=True)
    store = models.CharField(default="", max_length=255, blank=True, null=True)
    date = models.DateField(default=timezone.localdate, blank=True, null=True)
    time = models.TimeField(default=timezone.localtime, blank=True, null=True)
    detail = models.TextField(default="", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.description} - {self.amount} on {self.date}"
