from django.shortcuts import render

from opendp_apps.utils.random_gen import random_alphanum

def index(request):
    return render(request, 'async_messages/index.html')

def room(request, room_name):

    info = dict(room_name=f'{room_name}')
    return render(request, 'async_messages/room.html', info)