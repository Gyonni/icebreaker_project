from django.contrib import admin
from .models import PrayerRequest

@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    """
    관리자 페이지에서 익명 기도제목을 관리하기 위한 설정입니다.
    """
    # 목록 페이지에 보일 필드를 지정합니다.
    list_display = ('content', 'created_at')

    # 날짜를 기준으로 필터링할 수 있는 사이드바를 추가합니다.
    list_filter = ('created_at',)

    # 기도제목 내용으로 검색할 수 있는 검색창을 추가합니다.
    search_fields = ('content',)

    # Django의 기본 '선택한 항목 삭제' 액션을 사용합니다.
    # 이 설정이 있으면, 목록에서 항목을 체크한 뒤 '작업' 드롭다운에서 삭제를 선택할 수 있습니다.
    actions = ['delete_selected']