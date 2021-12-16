from django.urls import path
from . import views

app_name = "rooms"

# http://127.0.0.1:8000/rooms/1

urlpatterns = [
    path("<int:pk>",views.room_detail, name="detail")
]
