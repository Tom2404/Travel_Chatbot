from django.urls import path
from . import views
from . import auth_views

urlpatterns = [
    path("", views.index, name="index"),
    path("test/", views.test_view, name="test"),  # Test URL
    path("chat/", views.chat, name="chat"),
    path("chat/history/", views.chat_history, name="chat_history"),
    path("chat/clear/", views.clear_chat, name="clear_chat"),
    path("api/search/destinations/", views.search_destinations, name="search_destinations"),
    path("api/search/hotels/", views.search_hotels, name="search_hotels"),
    
    # Authentication URLs
    path("register/", auth_views.register_view, name="register"),
    path("login/", auth_views.login_view, name="login"),
    path("logout/", auth_views.logout_view, name="logout"),
    path("profile/", auth_views.profile_view, name="profile"),
    path("history/", auth_views.user_chat_history, name="user_history"),
]
