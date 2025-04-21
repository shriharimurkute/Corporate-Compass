"""
URL configuration for corporate_compass project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings           # Make sure settings is imported
from django.conf.urls.static import static # Import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('agencies/', include('agencies.urls')),
    path('complaints/', include('complaints.urls')),

    # Home Page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # Info Pages URLs
    path('info/government/', TemplateView.as_view(template_name='info/government.html'), name='info_government'),
    path('info/municipality/', TemplateView.as_view(template_name='info/municipality.html'), name='info_municipality'),
    path('info/city/', TemplateView.as_view(template_name='info/city.html'), name='info_city'),
    path('info/mayor/', TemplateView.as_view(template_name='info/mayor.html'), name='info_mayor'),
    path('info/issues/', TemplateView.as_view(template_name='info/issues.html'), name='info_issues'),
]

# Add this block to serve media files during development
if settings.DEBUG:
    # Use the static() function correctly
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Optional: If you are also serving static files collected to STATIC_ROOT in dev (less common)
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)