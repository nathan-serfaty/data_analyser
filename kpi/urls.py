from django.urls import path
from kpi import views # Importez vos vues
from django.conf import settings
from django.conf.urls.static import static
# Combine all your URL patterns into one list
urlpatterns = [
    path('', views.index, name='index'),  # Redirection vers l'application React
    path('upload/', views.file_upload_page, name='upload_page'),
    path('upload_file/', views.upload_file, name='upload_file'),
]

# Serve media files during development (debug mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
