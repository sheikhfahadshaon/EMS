from django.shortcuts import redirect, render, get_object_or_404
from .models import FoodItem, Order
from HOME.models import Event
from django.contrib import messages

def order_food(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    food_items = FoodItem.objects.all()  # You should filter this based on your requirements
    print(food_items)
    context = {
        'event': event,
        'food_items': food_items,
    }

    return render(request, 'order_food.html', context)

def order_place(request, food_item_id, event_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        # Retrieve the food item and event
        food_item = get_object_or_404(FoodItem, pk=food_item_id)
        event = get_object_or_404(Event, pk=event_id)

        # Create an order
        order = Order.objects.create(
            food_item=food_item,
            user=request.user,
            event=event,
            quantity=quantity
        )

        messages.success(request, 'Your order has been placed successfully!')
        return redirect('Cafeteria:order_success', event_id = event_id)

    else:
        food_item = get_object_or_404(FoodItem, pk=food_item_id)
        event = get_object_or_404(Event, pk=event_id)
        return render(request, 'order_food.html', {'food_item': food_item, 'event': event})

def order_success(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'order.html', {'event': event})

def order_list(request, event_id):
    orders = Order.objects.filter(event_id=event_id, user=request.user)
    event = Event.objects.get(pk=event_id)  # Make sure to import the Event model
    total_bill = 0
    for order in orders:
        order.total_price = order.food_item.price * order.quantity  # Calculate total price
        total_bill += order.total_price

    return render(request, 'order_list.html', {'orders': orders, 'event': event, 'total_bill': total_bill})

def cancel_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    # Check if the order belongs to the current user
    if order.user == request.user:
        order.delete()
        messages.success(request, 'Order canceled successfully!')
    else:
        messages.error(request, 'You can only cancel your own orders.')

    return redirect('Cafeteria:order_list', event_id=order.event.id)