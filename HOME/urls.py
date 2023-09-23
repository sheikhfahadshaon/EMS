from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name = 'home'),
    path('login/', views.log_in, name = 'LogIn'),
    path('signup/', views.sign_up, name = 'SignUp'),
    path('logout/', views.user_logout, name='logout'),
    path('addnewevent/', views.add_event, name='AddEvent'),
    path('Events/', views.event_list, name = 'Event_List'),
    path('eventupdate/<int:event_id>/', views.update_event, name='update_event'),
    path('eventdelete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('add_participant/<int:event_id>/', views.add_participant, name='add_participant'),
    path('eventdetail/<int:event_id>/', views.event_detail, name='event_detail'),
    path('view_profile/', views.view_profile, name='view_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('delete_profile/', views.delete_profile, name='delete_profile'),
    path('remove_participant/<int:event_id>/<int:user_id>/', views.remove_participant, name='remove_participant'),
    path('change_password', views.change_password, name = 'change_password'),
]