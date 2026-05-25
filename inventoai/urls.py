from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),        # landing, login, signup etc.
    path('accounts/', include('accounts.urls')),    # adjust as per your project
    path('store/', include('store.urls')),   # adjust as per your project
    path('ai/', include('ai_agent.urls')), # your AI agent app
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Also serve staticfiles automatically in dev (optional but convenient)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)