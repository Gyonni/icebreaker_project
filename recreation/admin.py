from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse
from .models import GameTeam, GameRoom, GameProblem, TeamSchedule
from profiles.models import Person
import random
import datetime

@admin.register(GameTeam)
class GameTeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'unique_code', 'score_display', 'current_round')
    list_editable = ('unique_code',)
    ordering = ['team_name']
    change_list_template = "admin/recreation/gameteam/change_list.html"

    def score_display(self, obj):
        if obj.end_time and obj.start_time:
            duration = obj.end_time - obj.start_time
            total_seconds = int(duration.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}분 {seconds}초"
        return "진행 중"
    score_display.short_description = "클리어 시간"

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        custom_urls = [
            path(
                'sync-teams/', 
                self.admin_site.admin_view(self.sync_teams_from_profiles), 
                name='%s_%s_sync_teams' % info
            ),
        ]
        return custom_urls + urls

    def sync_teams_from_profiles(self, request):
        profile_teams = Person.objects.values_list('team', flat=True).distinct()
        created_count = 0
        for team_name in profile_teams:
            if team_name:
                team, created = GameTeam.objects.get_or_create(team_name=team_name)
                if created:
                    created_count += 1
        
        self.message_user(request, f"{created_count}개의 새로운 팀을 동기화했습니다.")
        return HttpResponseRedirect("../")

@admin.register(GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_hint', 'location_answer', 'qr_code_id', 'view_qr_code_image', 'test_game_page')
    list_editable = ('location_hint', 'location_answer')
    readonly_fields = ('qr_code_id',)

    def view_qr_code_image(self, obj):
        url = reverse('recreation:generate_room_qr', args=[obj.qr_code_id])
        return format_html(f'<a href="{url}" target="_blank">QR 코드 보기</a>')
    view_qr_code_image.short_description = "QR 코드 (인쇄용)"

    def test_game_page(self, obj):
        url = reverse('recreation:play_game', args=[obj.qr_code_id])
        return format_html(f'<a href="{url}" target="_blank">테스트</a>')
    test_game_page.short_description = "게임 페이지"

@admin.register(GameProblem)
class GameProblemAdmin(admin.ModelAdmin):
    list_display = ('round_number', 'question', 'answer')
    ordering = ['round_number']

@admin.register(TeamSchedule)
class TeamScheduleAdmin(admin.ModelAdmin):
    list_display = ('round_number', 'team', 'room')
    list_filter = ('round_number', 'team', 'room')
    change_list_template = "admin/recreation/teamschedule/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        custom_urls = [
            path(
                'auto-generate/', 
                self.admin_site.admin_view(self.auto_generate_schedule_view), 
                name='%s_%s_auto_generate' % info
            ),
        ]
        return custom_urls + urls

    @transaction.atomic
    def auto_generate_schedule_view(self, request):
        teams = list(GameTeam.objects.all())
        mission_rooms = list(GameRoom.objects.exclude(name__in=['강당1', '주요한 목사님', '강당2']))
        
        if len(teams) == 0:
            self.message_user(request, "오류: 먼저 '게임 팀'을 등록해주세요.", messages.ERROR)
            return HttpResponseRedirect("../")

        TeamSchedule.objects.all().delete()

        try:
            room_round1 = GameRoom.objects.get(name='강당1')
            room_round4 = GameRoom.objects.get(name='주요한 목사님')
            room_round8 = GameRoom.objects.get(name='강당2')
        except GameRoom.DoesNotExist:
            self.message_user(request, "오류: '강당1', '주요한 목사님', '강당2' 장소가 먼저 등록되어야 합니다.", messages.ERROR)
            return HttpResponseRedirect("../")

        for team in teams:
            TeamSchedule.objects.create(team=team, round_number=1, room=room_round1)
            TeamSchedule.objects.create(team=team, round_number=4, room=room_round4)
            TeamSchedule.objects.create(team=team, round_number=8, room=room_round8)

        other_rounds = [2, 3, 5, 6, 7]
        num_teams = len(teams)
        num_mission_rooms = len(mission_rooms)

        for i in range(num_teams):
            team = teams[i]
            shuffled_rooms_for_team = list(mission_rooms)
            random.shuffle(shuffled_rooms_for_team)
            
            for j in range(len(other_rounds)):
                round_num = other_rounds[j]
                room = shuffled_rooms_for_team[j % num_mission_rooms]
                TeamSchedule.objects.create(team=team, round_number=round_num, room=room)

        self.message_user(request, "모든 팀의 스케줄을 성공적으로 자동 생성했습니다.", messages.SUCCESS)
        return HttpResponseRedirect("../")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        schedule_data = {}
        teams = GameTeam.objects.order_by('team_name')
        rounds = range(1, 9)
        
        for team in teams:
            schedule_data[team.team_name] = {}
            for round_num in rounds:
                schedule = TeamSchedule.objects.filter(team=team, round_number=round_num).first()
                schedule_data[team.team_name][round_num] = schedule.room.name if schedule else '-'

        extra_context['schedule_data'] = schedule_data
        extra_context['teams'] = teams
        extra_context['rounds'] = rounds
        
        return super().changelist_view(request, extra_context=extra_context)
