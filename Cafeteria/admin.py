from django.contrib import admin
from .models import FoodItem, Order
# Register your models here.
admin.site.register(FoodItem)
admin.site.register(Order)