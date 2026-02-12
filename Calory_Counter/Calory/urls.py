from django.urls import path
from . import views

urlpatterns=[

    path('',views.user_login,name='login'),

    path('register/',views.register),

    path('logout/',views.user_logout),

    path('profile/',views.profile,name='profile'),

    path('dashboard/',views.dashboard,name='dashboard'),

    path('add-meal/',views.add_meal),
    
    path("update-weight/", views.update_weight, name="update_weight"),
    
    path("summary/", views.summary_page, name="summary"),


    path("bot/", views.bot_page, name="bot_page"),

    path("bot/api/", views.bot_api, name="bot_api"),

]
