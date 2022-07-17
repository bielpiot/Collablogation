from django.urls import include, path

urlpatterns = {
    path('ap1/v1/', include('accounts.urls'))
}
