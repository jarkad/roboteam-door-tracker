from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.new_login, name="login"),
    path('logout', views.new_logout, name="logout"),
]


