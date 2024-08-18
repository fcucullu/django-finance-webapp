from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserPreferences(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    #Here add all the user preferences needed
    currency = models.CharField(default="EUR - Euro")
    currency_code = models.CharField(default="EUR")
    rows_per_page = models.IntegerField(default=25)

    def __str__(self):
        return f"{self.user.username}'s preferences" 