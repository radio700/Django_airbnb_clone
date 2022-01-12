from django.urls import path
from . import views

app_name = "reservations"

# http://127.0.0.1:8000/reservations/

urlpatterns = [
    path("create/<int:room>/<int:year>/<int:month>-<int:date>", views.create, name="create"),
]