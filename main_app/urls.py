from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('terms/', termspage, name="terms"),
    path('post-comment/', post_comment, name='post_comment'),
    #path('watch/<path:videourl>/<sandbox_attr>/', watchvideo, name="watchvideo"),
]
