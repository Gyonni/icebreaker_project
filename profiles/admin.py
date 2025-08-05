from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.db.models import Count, IntegerField
from django.db.models.functions import Cast
from django.utils.html import format_html
from django.http import HttpResponse
from .models import Person, Reaction, TmiRecommendation
import pandas as pd
import datetime
import qrcode
from io import BytesIO
from openpyxl.drawing.image import Image as OpenpyxlImage

@admin.action(description='선택된 참가자의 QR 정보를 엑셀로 내보내기')
def export_as_excel(modeladmin, request, queryset):
    data = []
    for person in queryset:
        profile_url = request.build_absolute_uri(
            reverse('profiles:profile_detail', args=[str(person.id)])
        )
        data.append({
            "고유번호": person.unique_code, "이름": person.name, "소속": person.group,
            "팀": person.team, "프로필 링크(QR내용)": profile_url,
        })
    df = pd.DataFrame(data)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Participants')
        worksheet = writer.sheets['Participants']
        worksheet.column_dimensions['A'].width = 15
        worksheet.column_dimensions['B'].width = 20
        worksheet.column_dimensions['C'].width = 20
        worksheet.column_dimensions['D'].width = 20
        worksheet.column_dimensions['E'].width = 60
        worksheet.column_dimensions['F'].width = 16
        worksheet.cell(row=1, column=6, value='QR Code 이미지')

        for index, person in enumerate(queryset):
            worksheet.row_dimensions[index + 2].height = 85
            qr_url = request.build_absolute_uri(reverse('profiles:profile_detail', args=[str(person.id)]))
            qr_img = qrcode.make(qr_url, box_size=3)
            img_buffer = BytesIO()
            qr_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            img = OpenpyxlImage(img_buffer)
            img.width = 105
            img.height = 105
            worksheet.add_image(img, f'F{index + 2}')
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
        person.scanned_by.clear()
    messages.success(request, f"{count}명의 '만난 사람' 목록을 성공적으로 초기화했습니다.")

@admin.action(description='선택된 참가자의 이모티콘 받은 개수 초기화')
def reset_emoji_counts(modeladmin, request, queryset):
    updated_count = queryset.update(
        emoji_laughed_count=0, emoji_touched_count=0,
        emoji_tmi_count=0, emoji_wow_count=0
    )
    Reaction.objects.filter(receiver__in=queryset).delete()
    messages.success(request, f"{updated_count}명의 이모티콘 받은 개수와 반응 기록을 초기화했습니다.")

@admin.action(description='선택된 참가자의 TMI 추천수 초기화')
def reset_tmi_recommendations(modeladmin, request, queryset):
    updated_count = queryset.update(tmi_recommend_count=0)
    TmiRecommendation.objects.filter(recommended__in=queryset).delete()
    messages.success(request, f"{updated_count}명의 TMI 추천수와 추천 기록을 초기화했습니다.")

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'numeric_unique_code',
        'group', 'team', 
        'tmi_recommend_count',
        'emoji_laughed_count', 'emoji_touched_count', 'emoji_tmi_count', 'emoji_wow_count',
        'is_authenticated', 
        'scanned_count',
        'view_qr_code'
    )
    list_filter = ('group', 'team', 'is_authenticated')
    search_fields = ('name', 'team', 'unique_code')
    actions = [
        reset_authentication, 
        reset_scanned_people, 
        export_as_excel, 
        reset_emoji_counts, 
        reset_tmi_recommendations
    ]
    change_list_template = "admin/profiles/person/change_list.html"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            numeric_code=Cast('unique_code', output_field=IntegerField()),
            num_scanned=Count('scanned_people', distinct=True)
        )
        return queryset

    @admin.display(description='고유번호', ordering='numeric_code')
    def numeric_unique_code(self, obj):
        return obj.unique_code

    @admin.display(description='만난 사람 수', ordering='num_scanned')
    def scanned_count(self, obj):
        return obj.num_scanned

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        custom_urls = [
            path('import_excel/', self.admin_site.admin_view(self.import_from_excel), name='%s_%s_import_excel' % info),
            path('export_excel_all/', self.admin_site.admin_view(self.export_all_participants), name='%s_%s_export_excel_all' % info),
        ]
        # [핵심 수정] 커스텀 URL과 기본 URL을 모두 반환하도록 수정합니다.
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
                    if not unique_code:
                        continue
                    
                    person, created = Person.objects.update_or_create(
                        unique_code=str(unique_code),
                        defaults={
                            'name': row['이름'], 'group': row['소속'], 'team': row['팀'],
                            'profile_image': None, 'bio_q1_answer': "", 'bio_q2_answer': "", 'bio_q3_answer': "",
                            'prayer_request': "", 'fun_fact': "", 'sentence1': "", 'sentence2': "", 'sentence3': "", 'sentence4': "",
                            'lie_answer': None, 'emoji_laughed_count': 0, 'emoji_touched_count': 0,
                            'emoji_tmi_count': 0, 'emoji_wow_count': 0, 'tmi_recommend_count': 0,
                            'was_picked': False, 'bingo_board_layout': [], 'is_authenticated': False, 'auth_token': None,
                        }
                    )
                    
                    person.scanned_people.clear()
                    person.scanned_by.clear()
                    Reaction.objects.filter(reactor=person).delete()
                    Reaction.objects.filter(receiver=person).delete()
                    TmiRecommendation.objects.filter(recommender=person).delete()
                    TmiRecommendation.objects.filter(recommended=person).delete()
                self.message_user(request, f"{len(df)}명의 참가자 정보가 성공적으로 등록/초기화되었습니다.")
            except Exception as e:
                self.message_user(request, f"파일 처리 중 오류가 발생했습니다: {e}", level=messages.ERROR)
            return redirect('..')
        return render(request, 'admin/profiles/person/import_excel_form.html', {"opts": self.model._meta})

    def view_qr_code(self, obj):
        try:
            url = reverse('profiles:generate_qr', args=[obj.id])
            return format_html('<a href="{}" target="_blank">QR코드 보기</a>', url)
        except Exception:
            return "URL 확인 필요"
    view_qr_code.short_description = "QR Code 생성"

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('receiver', 'reactor', 'emoji_type', 'timestamp')
    list_filter = ('emoji_type', 'receiver__name', 'reactor__name')
    search_fields = ('reactor__name', 'receiver__name')
    readonly_fields = ('reactor', 'receiver', 'emoji_type', 'timestamp')
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(TmiRecommendation)
class TmiRecommendationAdmin(admin.ModelAdmin):
    list_display = ('recommended', 'recommender', 'timestamp')
    list_filter = ('recommended__name', 'recommender__name')
    search_fields = ('recommended__name', 'recommender__name')
    readonly_fields = ('recommender', 'recommended', 'timestamp')
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
