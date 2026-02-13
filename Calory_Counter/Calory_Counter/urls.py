"""
URL configuration for Calory_Counter project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import include, path
# from django.conf import settings
# from django.conf.urls.static import static

# from . import views

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('home/', views.Home, name='home'),
#     path('about/', views.About, name='about'),
#     path('test/', include("Calory.urls"))
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect

def _redirect_to_app_login(request):
    return redirect('/')

urlpatterns = [
    # Redirect Django admin's login/logout (including querystring variants)
    re_path(r'^admin/login/?$', _redirect_to_app_login),
    re_path(r'^admin/logout/.*$', _redirect_to_app_login),

    path('admin/', admin.site.urls),
    path('admin-panel/', include('Admin.urls')),
    path('', include('Calory.urls')),
]
