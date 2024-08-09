from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('djoser.urls')),
    path('api/v1/auth/', include('djoser.urls')),
    path("account/", include("account.urls")),
    path("adminside/", include("adminside.urls")),
    path("dashboard/",include('dashboard.urls')),
    path('task_workers/', include('task_workers.urls')),
    path('profiles/', include('profiles.urls')),
    path('booking/', include('booking.urls')),
    path('api/chat/',include('chat.api.urls')),
    path('payments/', include('payments.urls')),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)