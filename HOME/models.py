from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_events')
    description = models.TextField()
    participants = models.ManyToManyField(User, blank=True, related_name='events_attending')

    def __str__(self):
        return self.name