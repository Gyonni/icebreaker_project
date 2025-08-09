from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse
from .models import GameTeam, GameRoom, GameProblem, TeamSchedule
from profiles.models import Person
import random

@admin.register(GameTeam)
class GameTeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'unique_code', 'score_display', 'current_round')
    # [수정] unique_code를 수정 가능하도록 readonly_fields에서 제거
    list_editable = ('unique_code',)
    ordering = ['team_name']

    def score_display(self, obj):
        if obj.end_time and obj.start_time:
            duration = obj.end_time - obj.start_time
            # 분과 초로 변환
            total_seconds = int(duration.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}분 {seconds}초"
        return "진행 중"
    score_display.short_description = "클리어 시간"

@admin.register(GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_hint', 'location_answer', 'qr_code_id')
    # [수정] 장소 힌트와 정답을 수정 가능하도록 추가
    list_editable = ('location_hint', 'location_answer')

@admin.register(GameProblem)
class GameProblemAdmin(admin.ModelAdmin):
    list_display = ('round_number', 'question', 'answer')
    # [수정] question과 completion_message는 텍스트 에디터로 편집하므로 list_editable에서 제외
    ordering = ['round_number']

@admin.action(description='팀별 스케줄 자동 생성하기')
@transaction.atomic
def auto_generate_schedule(modeladmin, request, queryset):
    teams = list(GameTeam.objects.all())
    # [수정] 1, 4, 8라운드 고정 장소를 제외한 나머지 미션방들을 가져옵니다.
    mission_rooms = list(GameRoom.objects.exclude(name__in=['강당1', '주요한 목사님', '강당2']))
    
    if len(teams) == 0:
        messages.error(request, "오류: 먼저 '게임 팀'을 등록해주세요.")
        return

    TeamSchedule.objects.all().delete()

    try:
        room_round1 = GameRoom.objects.get(name='강당1')
        room_round4 = GameRoom.objects.get(name='주요한 목사님')
        room_round8 = GameRoom.objects.get(name='강당2')
    except GameRoom.DoesNotExist:
        messages.error(request, "오류: '강당1', '주요한 목사님', '강당2' 장소가 먼저 등록되어야 합니다.")
        return

    # 1, 4, 8 라운드는 고정 장소로 배정
    for team in teams:
        TeamSchedule.objects.create(team=team, round_number=1, room=room_round1)
        TeamSchedule.objects.create(team=team, round_number=4, room=room_round4)
        TeamSchedule.objects.create(team=team, round_number=8, room=room_round8)

    # 나머지 5개 라운드(2,3,5,6,7) 스케줄 자동 생성
    other_rounds = [2, 3, 5, 6, 7]
    num_teams = len(teams)
    num_mission_rooms = len(mission_rooms)

    for i in range(num_teams):
        team = teams[i]
        # 각 팀별로 사용할 방 순서를 섞습니다.
        shuffled_rooms_for_team = list(mission_rooms)
        random.shuffle(shuffled_rooms_for_team)
        
        for j in range(len(other_rounds)):
            round_num = other_rounds[j]
            # 각 팀이 겹치지 않는 방을 순환하도록 배정합니다.
            room = shuffled_rooms_for_team[(i + j) % num_mission_rooms]
            TeamSchedule.objects.create(team=team, round_number=round_num, room=room)

    messages.success(request, "모든 팀의 스케줄을 성공적으로 자동 생성했습니다.")

@admin.register(TeamSchedule)
class TeamScheduleAdmin(admin.ModelAdmin):
    list_display = ('round_number', 'team', 'room')
    list_filter = ('round_number', 'team', 'room')
    actions = [auto_generate_schedule]

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