from django.urls import path
from . import views

urlpatterns=[

    path('',views.user_login,name='login'),

    path('register/',views.register),

    path('logout/',views.user_logout),

    path('profile/',views.profile,name='profile'),

    path('dashboard/',views.dashboard,name='dashboard'),

    path('add-meal/',views.add_meal),
    
    # Food management
    path('foods/', views.foods_list, name='foods_list'),
    path('foods/add/', views.add_food, name='add_food'),
    path('foods/edit/<int:food_id>/', views.edit_food, name='edit_food'),
    path('foods/delete/<int:food_id>/', views.delete_food, name='delete_food'),

    path("update-weight/", views.update_weight, name="update_weight"),

    path("bot/", views.bot_page, name="bot_page"),

    path("bot/api/", views.bot_api, name="bot_api"),

]
