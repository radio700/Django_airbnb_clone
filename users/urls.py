from django.urls import path
from . import views

app_name = "users"
# http://127.0.0.1:8000/users/login/

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.log_out, name="logout"),
    path("signup/", views.SignupView.as_view(), name="signup"),
]
