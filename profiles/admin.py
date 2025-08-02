from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.db.models import Count
from django.utils.html import format_html
from django.http import HttpResponse
from .models import Person, Reaction
import pandas as pd
import datetime
# --- [새로운 기능] QR코드 이미지 생성 및 엑셀 파일 조작을 위해 라이브러리 추가 ---
import qrcode
from io import BytesIO
from openpyxl.drawing.image import Image as OpenpyxlImage

# --- [수정] 엑셀 파일에 실제 QR 코드 이미지를 포함하도록 함수 수정 ---
@admin.action(description='선택된 참가자의 QR 정보를 엑셀로 내보내기')
def export_as_excel(modeladmin, request, queryset):
    # 1. 텍스트 데이터를 먼저 DataFrame으로 만듭니다.
    data = []
    for person in queryset:
        profile_url = request.build_absolute_uri(
            reverse('profiles:profile_detail', args=[str(person.id)])
        )
        data.append({
            "고유번호": person.unique_code,
            "이름": person.name,
            "소속": person.group,
            "팀": person.team,
            "프로필 링크(QR내용)": profile_url,
        })
    df = pd.DataFrame(data)

    # 2. 인메모리 버퍼에 엑셀 파일을 준비합니다.
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Participants')
        
        # 3. openpyxl 워크시트 객체를 가져와 직접 조작합니다.
        worksheet = writer.sheets['Participants']

        # 4. 열 너비를 설정하고 'QR Code 이미지' 헤더를 추가합니다.
        worksheet.column_dimensions['A'].width = 15
        worksheet.column_dimensions['B'].width = 20
        worksheet.column_dimensions['C'].width = 20
        worksheet.column_dimensions['D'].width = 20
        worksheet.column_dimensions['E'].width = 60
        # [수정] QR 코드 열의 너비를 16으로 늘립니다.
        worksheet.column_dimensions['F'].width = 16 
        worksheet.cell(row=1, column=6, value='QR Code 이미지')

        # 5. 각 참가자별로 QR 코드를 생성하고 이미지로 삽입합니다.
        for index, person in enumerate(queryset):
            # [수정] 행 높이를 85로 늘려 정사각형에 가까운 셀을 만듭니다.
            worksheet.row_dimensions[index + 2].height = 85

            # QR 코드의 내용이 '프로필 페이지 주소'가 되도록 수정합니다.
            profile_url = request.build_absolute_uri(
                reverse('profiles:profile_detail', args=[str(person.id)])
            )
            qr_img = qrcode.make(profile_url, box_size=3)
            
            # 이미지를 인메모리 버퍼에 저장
            img_buffer = BytesIO()
            qr_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)

            # openpyxl 이미지 객체를 생성하여 워크시트에 추가
            img = OpenpyxlImage(img_buffer)
            
            # ★★★ 핵심 수정: 이미지 크기를 105x105 픽셀로 고정합니다. ★★★
            img.width = 105
            img.height = 105
            
            worksheet.add_image(img, f'F{index + 2}')

    # 6. 완성된 엑셀 파일로 HTTP 응답을 생성합니다.
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    response['Content-Disposition'] = f'attachment; filename="participants_qr_{timestamp}.xlsx"'
    
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
    # [수정] list_display에 새로운 이모티콘 카운트 필드를 추가합니다.
    list_display = (
        'name', 'unique_code', 'group', 'team', 
        'emoji_laughed_count', 'emoji_touched_count', 'emoji_tmi_count', 'emoji_wow_count',
        'is_authenticated', 'scanned_count'
    )
    list_filter = ('group', 'team', 'is_authenticated')
    search_fields = ('name', 'team', 'unique_code')
    actions = [reset_authentication, reset_scanned_people, export_as_excel]
    change_list_template = "admin/profiles/person/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_from_excel), name='%s_%s_import_excel' % info),
            path('export-excel-all/', self.admin_site.admin_view(self.export_all_participants), name='%s_%s_export_excel_all' % info),
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

# --- [새로운 기능] Reaction 모델을 관리자 페이지에 등록 ---
@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    # 목록에 보일 필드들을 지정합니다.
    list_display = ('receiver', 'reactor', 'emoji_type', 'timestamp')
    # 필터 기능을 추가하여 특정 참가자나 이모티콘 종류별로 쉽게 찾아볼 수 있습니다.
    list_filter = ('emoji_type', 'receiver__name')
    # 검색 기능을 추가합니다.
    search_fields = ('reactor__username', 'receiver__name')
    # 관리자 페이지에서는 반응을 직접 추가/수정/삭제할 수 없도록 읽기 전용으로 설정합니다.
    readonly_fields = ('reactor', 'receiver', 'emoji_type', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False