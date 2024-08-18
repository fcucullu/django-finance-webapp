from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

# Create your models here.

class Income(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=now)
    description = models.TextField(max_length=50)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    account = models.CharField(max_length=255)

    def __str__(self):
        return self.category
    
    class Meta:
        ordering: ['-date']

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Account(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    
