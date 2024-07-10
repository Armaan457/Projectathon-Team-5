from django.db import models
# model for location access

class UniqueID(models.Model):
    unique_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7)
    longitude = models.DecimalField(max_digits=9, decimal_places=7)
    ip = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.unique_id
    




    