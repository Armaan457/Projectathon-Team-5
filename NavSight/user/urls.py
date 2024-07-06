from django.contrib import admin
from django.urls import path
from NavSight.user.views import yolo, blip

urlpatterns = [
    path('yolo/',yolo,name='yolo'),
    path('blip/',blip,name='blip'),
]