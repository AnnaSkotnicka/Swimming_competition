from django.db import models
from datetime import datetime
from django.utils import timezone


class Contestant(models.Model):
    objects = None
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=100)


class SwimmingTime(models.Model):
    objects = None
    swimming_track = models.CharField(max_length=2)
    contestant = models.ForeignKey(Contestant, on_delete=models.CASCADE)
    time_start = models.DateTimeField(max_length=30)
    time_stop = models.DateTimeField(max_length=30, null=True)

    def actual_time(self):
        if self.time_stop is not None:
            time = self.time_stop
        else:
            time = timezone.now()

        time_delta = time - self.time_start  # obiekt timedelta
        tmp = datetime(2023, 10, 17, 00, 00, 00, 00)
        time = time_delta + tmp  # obiekt datatime
        return time.strftime("%M:%S,%f")[:-4]





