from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('profiles/', include('profiles.urls')),
    # 'main.urls'를 'core.urls'로 수정하여 오류를 해결합니다.
    path('', include('core.urls')), 
]

# 개발 모드(DEBUG=True)일 때만 미디어 파일 URL을 추가합니다.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
