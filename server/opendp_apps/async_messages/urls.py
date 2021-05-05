from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile-test', views.view_profile_test, name='view_profile_test'),
    path('ajax-run-profile', views.ajax_profile_by_dataset_object_id, name='ajax_profile_by_dataset_object_id'),


    path('push-test', views.view_push_test, name='view_push_test'),
    path('test-room', views.view_room, name='view_room'),

]