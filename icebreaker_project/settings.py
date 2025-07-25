"""
Django settings for icebreaker_project project.
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^j!3z*^s$p!w8k(v1k+g#*h#7&!0s+7!b*#@y&o*#@y&o'

# ★★★★★ 핵심 수정 1: DEBUG 모드 활성화 ★★★★★
# 로컬에서 개발/테스트할 때는 반드시 True로 설정해야 합니다.
# True로 해야 에러의 상세 내용을 볼 수 있고, Django 개발 서버가 직접
# CSS/JS 같은 정적 파일들을 처리해줘서 화면 깨짐을 막아줍니다.
DEBUG = True

# 실제 서버 주소와 로컬 주소를 모두 허용합니다.
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '3.39.24.214',
    'jusarangxjesusvision.kr',
    'www.jusarangxjesusvision.kr',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'profiles',  # profiles 앱
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'icebreaker_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 프로젝트 전역에서 사용할 templates 폴더를 지정합니다.
        # 각 앱 안에 있는 templates 폴더는 APP_DIRS=True 설정으로 자동 인식됩니다.
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'icebreaker_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True


# ★★★★★ 핵심 수정 2: 정적 파일(Static files) 설정 정리 ★★★★★
# 겹치고 중복된 설정들을 모두 정리했습니다. 이것이 올바른 설정입니다.

# 1. 웹에서 정적 파일에 접근할 때 사용할 기본 URL 경로
STATIC_URL = 'static/'

# 2. 개발 서버가 CSS, JS, 이미지 파일 등을 찾을 '원본' 폴더들의 목록
#    - Django 관리자 페이지 스타일이 담긴 'staticfiles' 폴더
#    - 우리가 직접 만들 'main' 앱의 스타일이 담길 'main/static' 폴더
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfiles'),
    os.path.join(BASE_DIR, 'main', 'static'),
]

# 3. 실제 서버에 배포할 때, `collectstatic` 명령어로 모든 정적 파일을 '복사해서 모아둘 최종 폴더'
#    이 폴더 이름은 위의 STATICFILES_DIRS에 있는 폴더 이름과 절대로 겹치면 안 됩니다.
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'