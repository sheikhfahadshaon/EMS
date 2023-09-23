from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import *
from django.contrib.auth.decorators import login_required
from .models import Event
from django.contrib import messages
from django.utils import timezone
from datetime import date



def index(request):
    # Query the 5 most recent expired events
    expired_events = Event.objects.filter(start_date__lt=date.today()).order_by('-start_date')[:5]

    return render(request, 'index.html', {'expired_events': expired_events})


def log_in(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a success page or user's profile
                return redirect('home')
            else:
                # Authentication failed, display an error message
                form.add_error(None, 'Invalid username or password. Please try again.')
    else:
        form = UserLoginForm()

    return render(request, 'Login.html', {'form': form})


def sign_up(request):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # Refresh the user object from the database
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            login(request, user)
            return redirect('home')

    else:
        form = UserSignUpForm()
    return render(request, 'SignUp.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')

# views.py

# Helper function to check for time conflicts
def has_time_conflict(event, events_on_date):
    event_start_time = event.start_time
    event_end_time = event.end_time

    for other_event in events_on_date:
        if event != other_event:
            other_start_time = other_event.start_time
            other_end_time = other_event.end_time

            # Check if the event's start_time or end_time falls within the range of other_event's time
            if (event_start_time >= other_start_time and event_start_time <= other_end_time) or \
               (event_end_time >= other_start_time and event_end_time <= other_end_time):
                return True

    return False
def add_event(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You need to log in first')
        return redirect('home')

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.host = request.user

            # Fetch events on the same date as the new event
            events_on_date = Event.objects.filter(
                start_date=new_event.start_date
            )

            # Check for time conflicts
            if not has_time_conflict(new_event, events_on_date):
                new_event.save()
                return redirect('Event_List')
            else:
                messages.error(request, 'There is a time conflict with another event on the same date.')
        else:
            messages.error(request, 'Invalid form data. Please check the form and try again.')
    else:
        form = EventForm()

    return render(request, 'add_event.html', {'form': form})
@login_required
def update_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.user == event.host:
        if request.method == 'POST':
            form = EventForm(request.POST, instance=event)
            if form.is_valid():
                updated_event = form.save(commit=False)

                # Fetch events on the same date as the updated event
                events_on_date = Event.objects.filter(
                    host=request.user,
                    start_date=updated_event.start_date
                )

                # Exclude the current event being updated
                events_on_date = events_on_date.exclude(pk=event.id)

                # Check for time conflicts
                if not has_time_conflict(updated_event, events_on_date):
                    updated_event.save()
                    return redirect('event_list')
                else:
                    messages.error(request, 'There is a time conflict with another event on the same date.')
            else:
                messages.error(request, 'Invalid form data. Please check the form and try again.')
        else:
            form = EventForm(instance=event)
        return render(request, 'update_event.html', {'form': form, 'event': event})
    else:
        return redirect('Event_List')

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.user == event.host:
        if request.method == 'POST':
            event.delete()
            return redirect('Event_List')
        return render(request, 'delete_event.html', {'event': event})
    else:
        return redirect('Event_List')

def event_list(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You need to log in first')
        return redirect('home')
    current_datetime = timezone.now()
    events = Event.objects.filter(start_date__gte=current_datetime.date(), start_time__gte=current_datetime.time())
    return render(request, 'event_list.html', {'events': events})

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    participants = event.participants.all()
    return render(request, 'event_detail.html', {'event': event, 'participants': participants})


@login_required
def add_participant(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    # Check if the user is already a participant
    if request.user == event.host or request.user in event.participants.all():
        messages.warning(request, 'You are already a participant in this event.')
    else:
        event.participants.add(request.user)
        messages.success(request, 'You have successfully joined the event as a participant.')

    return redirect('Event_List')


@login_required
def view_profile(request):
    user = request.user
    hosted_events = Event.objects.filter(host=user)
    participating_events = Event.objects.filter(participants=user)
    return render(request, 'view_profile.html', {'hosted_events': hosted_events, 'participating_events': participating_events})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def delete_profile(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('logout')  # Redirect to logout view
    return render(request, 'delete_profile.html')


@login_required
def remove_participant(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    # Check if the user is a participant in the event
    if request.user in event.participants.all():
        event.participants.remove(request.user)
        messages.success(request, 'You have been removed from the event participants.')
    else:
        messages.warning(request, 'You are not a participant in this event.')

    return redirect('Event_List')

@login_required
def change_password(request):
    user = request.user

    if request.method == 'POST':
        form = ChangePasswordForm(user, request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Invalid old password.')
    else:
        form = ChangePasswordForm(user, request.POST)

    context = {'form': form}
    return render(request, 'change_password.html', context)