from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("test/", views.test_view, name="test"),  # Test URL
    path("chat/", views.chat, name="chat"),
    path("chat/history/", views.chat_history, name="chat_history"),
]
