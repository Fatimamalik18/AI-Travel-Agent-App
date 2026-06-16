from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Accounts app (login, signup, users APIs sab yahan se aayenge)
    path('api/acc/', include('accounts.urls')),
]

# Media files serve karne ke liye
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)