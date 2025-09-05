from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('person/<str:name>', views.getPerson, name='name'),
    path('latestLogs', views.logs, name='logs'),
]
