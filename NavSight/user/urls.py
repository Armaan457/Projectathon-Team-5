from django.contrib import admin
from django.urls import path
from NavSight.user.views import yolo, blip
from .import views
from django.urls import path
from . import views
from django.conf.urls.static import static 
from django.conf import settings 


urlpatterns = [
    path('yolo/',yolo,name='yolo'),
    path('blip/',blip,name='blip'),
    path('', views.members, name='members'),
    path("words" , views.number, name="number"),
    path('home/',views.home,name="home"),
    path('unique_id' , views.id,name="id"),
    path('log_signup/', views.log_signup, name='log_signup'),
    path('login', views.login, name="login"),
    path('signup', views.signup, name='signup'),
    path('uniqueid1',views.uniqueid1 , name="uniqueid1"),
    path('uniqueid2' , views.uniqueid2 , name="uniqueid2"),
    path('navigatorhome' , views.navigatorhome , name="navigatorhome"),
    path('location',views.location ,name="location")
] 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)