"""
URL configuration for icebreaker_project project.

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
# include를 import 목록에 추가해주세요.
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    # 'profiles/'로 시작하는 모든 주소(URL)는 이제부터 profiles/urls.py 파일이 담당하게 됩니다.
    path('profiles/', include('profiles.urls')), 
]
