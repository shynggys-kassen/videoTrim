from django.contrib import admin
from django.urls import path, include
from .views import TrimLocally, TrimInternet

urlpatterns = [
    path('trimLocally/', TrimLocally.as_view(), name="trimLocally"),
    path('trimInternet/', TrimInternet.as_view(), name="trimInternet"),
]