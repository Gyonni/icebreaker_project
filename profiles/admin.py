from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.db.models import Count
from django.utils.html import format_html
from django.http import HttpResponse
from .models import Person
import pandas as pd
import datetime

@admin.action(description='선택된 참가자의 QR 정보를 엑셀로 내보내기')
def export_as_excel(modeladmin, request, queryset):
    data = []
    for person in queryset:
        profile_url = request.build_absolute_uri(
            reverse('profiles:profile_detail', args=[str(person.id)])
        )
        data.append({
            "고유번호": person.unique_code, "이름": person.name, "소속": person.group,
            "팀": person.team, "QR코드 링크": profile_url,
        })
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    response['Content-Disposition'] = f'attachment; filename="participants_qr_{timestamp}.xlsx"'
    df.to_excel(response, index=False, engine='openpyxl')
    return response

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
    list_display = ('name', 'unique_code', 'group', 'team', 'is_authenticated', 'scanned_count', 'view_qr_code')
    list_filter = ('group', 'team', 'is_authenticated')
    search_fields = ('name', 'team', 'unique_code')
    actions = [reset_authentication, reset_scanned_people, export_as_excel]
    change_list_template = "admin/profiles/person/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # [수정] URL 이름에서 하이픈(-)을 언더스코어(_)로 변경
            path('import-excel/', self.admin_site.admin_view(self.import_from_excel), name='import_excel'),
            path('export-excel-all/', self.admin_site.admin_view(self.export_all_participants), name='export_excel_all'),
        ]
        return custom_urls + urls

    def export_all_participants(self, request):
        queryset = Person.objects.all()
        return export_as_excel(self, request, queryset)

    def import_from_excel(self, request):
        if request.method == 'POST':
            excel_file = request.FILES.get("excel_file")
            if not excel_file:
                self.message_user(request, "엑셀 파일을 선택해주세요.", level=messages.ERROR)
                return redirect('.')
            try:
                df = pd.read_excel(excel_file, engine='openpyxl')
                required_columns = ['고유번호', '이름', '소속', '팀']
                if not all(col in df.columns for col in required_columns):
                    missing_cols = [col for col in required_columns if col not in df.columns]
                    self.message_user(request, f"엑셀 파일에 다음 필수 컬럼이 없습니다: {', '.join(missing_cols)}", level=messages.ERROR)
                    return redirect('.')
                for index, row in df.iterrows():
                    unique_code = row.get('고유번호')
                    if not unique_code: continue
                    Person.objects.update_or_create(
                        unique_code=str(unique_code),
                        defaults={
                            'name': row['이름'], 'group': row['소속'], 'team': row['팀'],
                            'bio': row.get('소개', ''), 'fun_fact': row.get('재미있는 사실', '')
                        }
                    )
                self.message_user(request, "엑셀 파일로부터 성공적으로 사용자들을 추가/업데이트했습니다.")
            except Exception as e:
                self.message_user(request, f"파일 처리 중 오류가 발생했습니다: {e}", level=messages.ERROR)
            return redirect('..')
        return render(request, 'admin/profiles/person/import_excel_form.html', {"opts": self.model._meta})

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
