from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.db.models import Count
from django.utils.html import format_html
from .models import Person
import pandas as pd

@admin.action(description='선택된 사용자의 인증 상태 초기화')
def reset_authentication(modeladmin, request, queryset):
    updated_count = queryset.update(is_authenticated=False, auth_token=None)
    messages.success(request, f"{updated_count}명의 사용자의 인증 상태를 초기화했습니다.")

@admin.action(description='선택된 사용자의 만난 사람 목록 초기화')
def reset_scanned_people(modeladmin, request, queryset):
    count = len(queryset)
    for person in queryset:
        person.scanned_people.clear()
    messages.success(request, f"{count}명의 '만난 사람' 목록을 성공적으로 초기화했습니다.")

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    # 고유번호를 표시하고 검색할 수 있도록 수정했습니다.
    list_display = ('name', 'unique_code', 'group', 'team', 'is_authenticated', 'scanned_count', 'view_qr_code')
    list_filter = ('group', 'team', 'is_authenticated')
    search_fields = ('name', 'team', 'unique_code')
    actions = [reset_authentication, reset_scanned_people]
    change_list_template = "admin/profiles/person/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_from_excel), name='import-excel'),
        ]
        return custom_urls + urls

    def import_from_excel(self, request):
        if request.method == 'POST':
            if 'excel_file' not in request.FILES:
                self.message_user(request, "엑셀 파일을 선택해주세요.", level=messages.ERROR)
                return redirect('.')
            
            excel_file = request.FILES['excel_file']
            try:
                df = pd.read_excel(excel_file, engine='openpyxl')
                # 엑셀 파일에 '고유번호' 컬럼이 필수로 포함되어야 합니다.
                required_columns = ['고유번호', '이름', '소속', '팀']
                if not all(col in df.columns for col in required_columns):
                    missing_cols = [col for col in required_columns if col not in df.columns]
                    self.message_user(request, f"엑셀 파일에 다음 필수 컬럼이 없습니다: {', '.join(missing_cols)}", level=messages.ERROR)
                    return redirect('.')

                for index, row in df.iterrows():
                    unique_code = row.get('고유번호')
                    if not unique_code:
                        continue
                    
                    # 고유번호를 기준으로 사용자를 찾아 업데이트합니다.
                    Person.objects.update_or_create(
                        unique_code=unique_code,
                        defaults={
                            'name': row['이름'],
                            'group': row['소속'],
                            'team': row['팀'],
                            'bio': row.get('소개', ''),
                        }
                    )
                self.message_user(request, "엑셀 파일로부터 성공적으로 사용자들을 추가/업데이트했습니다.")
            except Exception as e:
                self.message_user(request, f"파일 처리 중 오류가 발생했습니다: {e}", level=messages.ERROR)
            
            return redirect('..')

        return render(
            request, 'admin/profiles/person/import_excel_form.html', context={"opts": self.model._meta}
        )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_scanned_count=Count('scanned_people', distinct=True))

    def scanned_count(self, obj):
        return obj._scanned_count
    scanned_count.short_description = '만난 사람 수'
    scanned_count.admin_order_field = '_scanned_count'

    def view_qr_code(self, obj):
        try:
            url = reverse('profiles:generate_qr', args=[obj.id])
            return format_html('<a href="{}" target="_blank">QR코드 보기</a>', url)
        except Exception:
            return "URL 확인 필요"
    
    view_qr_code.short_description = "QR Code 생성"
