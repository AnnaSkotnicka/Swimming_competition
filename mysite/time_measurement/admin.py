from django.contrib import admin
from .models import Contestant, SwimmingTime

# Register your models here.
admin.site.register(Contestant)
admin.site.register(SwimmingTime)