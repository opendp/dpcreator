from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('push-test', views.push_test, name='push_test'),
    path('<str:room_name>/', views.room, name='room'),

]