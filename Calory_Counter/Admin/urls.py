from django.urls import path
from . import views

urlpatterns = [
    # Admin Authentication
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    
    # Admin Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Food Management
    path('foods/', views.manage_foods, name='admin_manage_foods'),
    path('foods/add/', views.add_food_admin, name='admin_add_food'),
    path('foods/edit/<int:food_id>/', views.edit_food_admin, name='admin_edit_food'),
    path('foods/delete/<int:food_id>/', views.delete_food_admin, name='admin_delete_food'),
    
    # User Management
    path('users/', views.manage_users, name='admin_manage_users'),
    path('users/toggle-admin/<int:user_id>/', views.toggle_admin, name='admin_toggle_admin'),
    
    # Admin Management
    path('admins/', views.manage_admins, name='admin_manage_admins'),
    path('admins/edit-role/<int:admin_id>/', views.edit_admin_role, name='admin_edit_role'),
]
