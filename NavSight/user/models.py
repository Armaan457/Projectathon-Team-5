from django.db import models

# Create your models here.
class user_details(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    phone = models.PositiveIntegerField()
    email = models.CharField(max_length=50)


    