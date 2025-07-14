from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.shortcuts import render

# Custom 404 view
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

handler404 = 'project.urls.custom_404_view'

# URL patterns
urlpatterns = [
    path('adminsecure/', admin.site.urls),
    path('', include('app.urls')),
]

# Serve media files (uploads) – this works for both DEBUG=True and False (only for local testing)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Optional: serve static files as well if needed (only for local testing)
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
