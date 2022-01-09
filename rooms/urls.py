from django.urls import path
from . import views

app_name = "rooms"

# http://127.0.0.1:8000/rooms/

urlpatterns = [
    # path("<int:pk>",views.room_detail, name="detail"),
    path("<int:pk>/", views.RoomDetail.as_view(), name="detail"),
    path("<int:pk>/edit/", views.EditRoomView.as_view(), name="edit"),
    path("<int:pk>/photos/", views.RoomPhotosview.as_view(), name="photos"),
    path("search/", views.search, name="search"),

]
