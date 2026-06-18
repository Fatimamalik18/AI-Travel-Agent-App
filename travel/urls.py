from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    # Accounts APIs
    path('api/acc/', include('accounts.urls')),

    # Itineraries APIs
    path('api/itineraries/', include('itineraries.urls')),
]


# Media files serve karne ke liye
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)