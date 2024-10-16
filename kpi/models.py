from django.db import models

# Create your models here.
from django.db import models

class KPI(models.Model):
    name = models.CharField(max_length=100)
    value = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

