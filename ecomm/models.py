from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('shopkeeper', 'Shopkeeper'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} - {self.role}"
class inventory(models.Model):
    name = models.CharField(max_length=20)
    category=models.CharField(max_length=20)
    price=models.FloatField()
    quantity=models.IntegerField()
    description=models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    restocked_at = models.DateTimeField(auto_now=True)


