from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('push-test', views.view_push_test, name='view_push_test'),
    path('test-room', views.view_room, name='view_room'),

]