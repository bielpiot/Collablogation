from django.contrib import admin
from django.urls import path, include

patterns = [
    path('account/', include('accounts.urls')),
    path('', include('api.urls'))
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/", include(patterns)),
]
