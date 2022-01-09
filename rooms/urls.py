from django.urls import path
from . import views

app_name = "rooms"

# http://127.0.0.1:8000/rooms/

urlpatterns = [
    # path("<int:pk>",views.room_detail, name="detail"),
    path("create/", views.CreateRoomView.as_view(), name="create"),
    
    path("<int:pk>/", views.RoomDetail.as_view(), name="detail"),
    path("<int:pk>/edit/", views.EditRoomView.as_view(), name="edit"),
    path("<int:pk>/photos/", views.RoomPhotosview.as_view(), name="photos"),

    path("<int:pk>/photos/add", views.AddPhotoview.as_view(), name="add-photos"),
    path("<int:room_pk>/photos/<int:photo_pk>/delete/", views.delete_photo, name="delete-photos"),
    path("<int:room_pk>/photos/<int:photo_pk>/edit/", views.EditPhotoView.as_view(), name="edit-photos"),
    path("search/", views.search, name="search"),

]
