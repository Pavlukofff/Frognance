"""
URL configuration for frognance project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from accounts.views import home
from finance.api_views import IncomeListAPI

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('', include('accounts.urls')),
    path('finance/', include('finance.urls')),
    
    # API routes
    path('api/income/', IncomeListAPI.as_view(), name='api_income_list'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
