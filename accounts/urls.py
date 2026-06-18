from django.urls import path
from .views import UserListCreateView, UserDetailView, LoginView

urlpatterns = [
   
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    
    path('users/<uuid:pk>/', UserDetailView.as_view(), name='user-detail'),
     path("login/", LoginView.as_view(), name="login"),
]