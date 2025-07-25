from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.db.models import Count
from django.utils.html import format_html
from .models import Person
import pandas as pd # pandas가 더 안정적이고 다양한 엑셀 형식을 지원합니다.

# Admin Action: 선택된 사용자의 인증 상태 초기화
@admin.action(description='선택된 사용자의 인증 상태 초기화')
def reset_authentication(modeladmin, request, queryset):
    updated_count = queryset.update(is_authenticated=False, auth_token=None)
    messages.success(request, f"{updated_count}명의 사용자의 인증 상태를 초기화했습니다.")

# Admin Action: 선택된 사용자의 만난 사람 목록 초기화
@admin.action(description='선택된 사용자의 만난 사람 목록 초기화')
def reset_scanned_people(modeladmin, request, queryset):
    count = len(queryset)
    for person in queryset:
        person.scanned_people.clear()
    messages.success(request, f"{count}명의 '만난 사람' 목록을 성공적으로 초기화했습니다.")

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    # models.py에 정의된 필드에 맞춰 list_display를 수정했습니다.
    list_display = ('name', 'team', 'role', 'group', 'is_authenticated', 'scanned_count', 'view_qr_code')
    list_filter = ('team', 'role', 'group', 'is_authenticated')
    search_fields = ('name', 'phone_number', 'team')
    actions = [reset_authentication, reset_scanned_people]
    change_list_template = "admin/profiles/person/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # import-excel URL은 그대로 유지합니다.
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
                # pandas를 사용하여 엑셀 파일 읽기
                df = pd.read_excel(excel_file, engine='openpyxl')

                # models.py에 맞는 필수 컬럼을 확인합니다.
                required_columns = ['이름', '팀', '역할', '전화번호', '소속']
                if not all(col in df.columns for col in required_columns):
                    self.message_user(request, f"엑셀 파일에 다음 필수 컬럼이 모두 포함되어 있는지 확인해주세요: {', '.join(required_columns)}", level=messages.ERROR)
                    return redirect('.')

                for index, row in df.iterrows():
                    # 전화번호는 고유값이므로 데이터 처리의 기준이 됩니다.
                    phone_number = ''.join(filter(str.isdigit, str(row['전화번호'])))
                    if not phone_number:
                        continue # 전화번호가 없으면 건너뜁니다.
                    
                    # Person 객체 생성 또는 업데이트 (고유값인 phone_number 기준)
                    Person.objects.update_or_create(
                        phone_number=phone_number,
                        defaults={
                            'name': row['이름'],
                            'team': row['팀'],
                            'role': row['역할'],
                            'group': row['소속'],
                            'bio': row.get('소개', ''), # '소개' 컬럼은 선택사항
                        }
                    )
                self.message_user(request, "엑셀 파일로부터 성공적으로 사용자들을 추가/업데이트했습니다.")
            except Exception as e:
                self.message_user(request, f"파일 처리 중 오류가 발생했습니다: {e}", level=messages.ERROR)
            
            return redirect('..')

        # GET 요청 시, 템플릿을 렌더링합니다.
        # 템플릿 경로를 올바르게 수정했습니다.
        return render(
            request, 'admin/profiles/person/import_excel_form.html', context={"opts": self.model._meta}
        )

    # '만난 사람 수'를 계산하기 위한 로직
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_scanned_count=Count('scanned_people', distinct=True))

    def scanned_count(self, obj):
        return obj._scanned_count
    scanned_count.short_description = '만난 사람 수'
    scanned_count.admin_order_field = '_scanned_count'

    # QR 코드 보기 링크
    def view_qr_code(self, obj):
        # 'profiles' 앱의 urls.py에 'generate_qr'이라는 이름의 URL 패턴이 있어야 합니다.
        try:
            url = reverse('profiles:generate_qr', args=[obj.pk])
            return format_html('<a href="{}" target="_blank">QR코드 보기</a>', url)
        except Exception:
            return "URL 확인 필요"
    
    view_qr_code.short_description = "QR Code 생성"