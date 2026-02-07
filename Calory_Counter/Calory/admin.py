from django.contrib import admin
from .models import *

admin.site.register(Profile)
admin.site.register(Food)
admin.site.register(Meal)
admin.site.register(DailySummary)

