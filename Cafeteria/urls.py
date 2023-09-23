from django.urls import path
from . import views

app_name = 'Cafeteria'

urlpatterns = [
    path('order_food/<int:event_id>/', views.order_food, name='order_food'),
    path('order/<int:food_item_id>/<int:event_id>/', views.order_place, name='order_place'),
    path('order/success/<int:event_id>/', views.order_success, name='order_success'),
    path('cafeteria/order/list/<int:event_id>/', views.order_list, name='order_list'),
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
]
