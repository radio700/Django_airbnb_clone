from django.shortcuts import render

# Create your views here.

def create(request, room, year, month, day):
    print(room, year, month, day)