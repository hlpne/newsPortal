"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from news.views import NewsListView
from oauth_views import google_login_direct, yandex_login_direct

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', NewsListView.as_view(), name='home'),  # Show news on root URL
    path('protect/', include('protect.urls')),  # Move protect to /protect/
    path('sign/', include('sign.urls')),
    path('accounts/', include('allauth.urls')),
    path('news/', include('news.urls')),
    
    # Direct OAuth redirects
    path('oauth/google/', google_login_direct, name='google_direct'),
    path('oauth/yandex/', yandex_login_direct, name='yandex_direct'),
]
