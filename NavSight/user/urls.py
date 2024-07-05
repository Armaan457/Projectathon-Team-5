from django.contrib import admin
from django.urls import path
from NavSight.user.views import yolo

urlpatterns = [
    path('yolo/',yolo,name='yolo')
]