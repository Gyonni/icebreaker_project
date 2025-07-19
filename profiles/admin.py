from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from django.utils.html import format_html
from django.urls import reverse
from .models import Person
import openpyxl

@admin.action(description='선택된 사용자의 인증 상태 초기화')
def reset_authentication(modeladmin, request, queryset):
    queryset.update(is_authenticated=False, auth_token=None)

# ★★★★★ 새로운 액션 함수 정의 ★★★★★
@admin.action(description='선택된 사용자의 만난 사람 목록 초기화')
def reset_scanned_people(modeladmin, request, queryset):
    for person in queryset:
        person.scanned_people.clear()
    messages.success(request, "선택된 사용자들의 '만난 사람' 목록을 성공적으로 초기화했습니다.")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'is_authenticated', 'scanned_count', 'view_qr_code')
    search_fields = ('name',)
    # ★★★★★ actions 리스트에 새로운 액션 추가 ★★★★★
    actions = [reset_authentication, reset_scanned_people]
    change_list_template = "admin/profiles/person/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.import_from_excel, name='import_excel'),
        ]
        return custom_urls + urls

    def import_from_excel(self, request):
        if request.method == "POST":
            excel_file = request.FILES["excel_file"]
            try:
                wb = openpyxl.load_workbook(excel_file)
                sheet = wb.active
                
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    name, age, bio, fun_fact = row
                    if name:
                        Person.objects.update_or_create(
                            name=name,
                            defaults={
                                'age': age if age else None,
                                'bio': bio if bio else "",
                                'fun_fact': fun_fact if fun_fact else ""
                            }
                        )
                messages.success(request, "엑셀 파일로부터 프로필이 성공적으로 등록/업데이트되었습니다.")
                return redirect("..")
            except Exception as e:
                messages.error(request, f"파일 처리 중 오류가 발생했습니다: {e}")

        return render(request, "admin/import_excel_form.html")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_scanned_count=Count('scanned_people'))

    def scanned_count(self, obj):
        return obj._scanned_count
    scanned_count.short_description = '만난 사람 수'
    scanned_count.admin_order_field = '_scanned_count'

    def view_qr_code(self, obj):
        url = reverse('profiles:generate_qr', args=[obj.pk])
        return format_html('<a href="{}" target="_blank">QR코드 보기</a>', url)
    
    view_qr_code.short_description = "QR Code 생성"