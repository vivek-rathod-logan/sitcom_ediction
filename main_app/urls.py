from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('watch/<path:videourl>/<sandbox_attr>/', watchvideo, name="watchvideo"),
]
