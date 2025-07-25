"""
Django settings for icebreaker_project project.
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# 실제 운영 환경에서는 이 키를 코드에 직접 쓰지 않고 숨겨야 합니다.
SECRET_KEY = 'django-insecure-^j!3z*^s$p!w8k(v1k+g#*h#7&!0s+7!b*#@y&o*#@y&o'

# ★★★★★ 중요: 실제 서버에서는 반드시 False로 설정해야 합니다. ★★★★★
# False로 해야 보안이 강화되고, Nginx가 정적 파일을 처리하게 됩니다.
DEBUG = False

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
    'profiles',
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
        'DIRS': [],
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

# --- ★★★★★ 핵심 수정: 정적 파일 및 미디어 파일 설정 최종 정리 ★★★★★ ---

# 1. Static files (CSS, JavaScript, Admin Images)
STATIC_URL = '/static/'
# 'collectstatic' 명령어가 모든 정적 파일을 복사해서 모아둘 최종 폴더
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 2. Media files (User-uploaded profile images)
MEDIA_URL = '/media/'
# 사용자가 업로드한 프로필 사진이 실제로 저장될 폴더
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
