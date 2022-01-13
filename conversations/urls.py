from django.urls import path
from . import views

app_name = 'conversations'
#http://127.0.0.1:8000/conversations

urlpatterns = [
    path('go/<int:a_pk>/<int:b_pk>/', views.go_conversation, name='go_conversation'),
    path('<int:pk>/', views.ConversationDetailView.as_view(), name='detail'),
]