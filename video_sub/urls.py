from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('video.urls', namespace="videos" )),
    path('courses/', include('courses.urls', namespace='courses')),

    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns  += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
