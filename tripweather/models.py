import django
import uuid

from django.db import models
from django.urls import reverse


class Trip(models.Model):
    unique_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=256)
    start_loc = models.CharField(max_length=50)
    end_loc = models.CharField(max_length=50)
    date = models.DateTimeField(default=django.utils.timezone.now())
    deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Trip"
        verbose_name_plural = "Trips"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('check_weather', kwargs={"unique_id": self.unique_id})
