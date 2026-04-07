from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('complaints.urls')),
    path('api/', include('complaints.api_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Barangay Portal Admin"
admin.site.site_title = "Barangay Portal"