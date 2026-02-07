from django.urls import path
from . import views


urlpatterns = [
    path('abc/', views.Home, name='home'),
]