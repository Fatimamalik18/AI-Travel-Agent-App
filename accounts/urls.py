from django.urls import path
from .views import (
    UserListCreateView,
    UserDetailView,
    LoginView,
    SignupView,
    InterestListCreateView,  # naya import
    InterestDetailView,       # naya import
    UserPreferencesView,
    UserProfileView, 
    NotificationListCreateView,   # naya import
    NotificationDetailView ,       # naya import
    UpdateNotification
)

urlpatterns = [

    # Users APIs
    path(
        'users/',
        UserListCreateView.as_view(),
        name='user-list-create'
    ),

    path(
        'users/<uuid:pk>/',
        UserDetailView.as_view(),
        name='user-detail'
    ),

    # Login API
    path(
        'login/',
        LoginView.as_view(),
        name='login'
    ),

    # Signup API
    path(
        'signup/',
        SignupView.as_view(),
        name='signup'
    ),
    
     # Interest APIs  ← naye URLs
    path('interests/', InterestListCreateView.as_view(), name='interest-list-create'),
    path('interests/<uuid:pk>/', InterestDetailView.as_view(), name='interest-detail'),
    
    
    # User Preferences API
    path('preferences/', UserPreferencesView.as_view(), name='user-preferences'),
    
     # Profile API  
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('notifications/<uuid:pk>/update/', UpdateNotification.as_view(), name='update-notification'),
    # Notification APIs  ← naye
    path('notifications/', NotificationListCreateView.as_view(), name='notification-list-create'),
    path('notifications/<uuid:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
]

