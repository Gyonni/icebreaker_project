# core/views.py
from django.shortcuts import render

def index(request):
    # 홈페이지를 보여주는 함수
    return render(request, 'core/index.html')

def schedule(request):
    # 수련회 일정 페이지를 보여주는 함수
    return render(request, 'core/schedule.html')
