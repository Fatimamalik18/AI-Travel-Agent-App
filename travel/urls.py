from django.contrib import admin
from django.urls import path,include
from django.db import models
from accounts.models import CustomUser

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/acc/', include('accounts.urls')),
    path('api/trip/', include('trip.urls')),
    path('api/destination/', include('destination.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)