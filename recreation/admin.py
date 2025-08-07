# recreation/admin.py
from django.contrib import admin, messages
from django.db import transaction
from django.utils.html import format_html
from django.urls import reverse
from .models import GameTeam, GameRoom, GameProblem, GameTimeSlot, TeamSchedule
from profiles.models import Person
import random

@admin.action(description='프로필 앱의 팀 목록과 동기화하기')
def sync_teams_from_profiles(modeladmin, request, queryset):
    profile_teams = Person.objects.values_list('team', flat=True).distinct()

    created_count = 0
    for team_name in profile_teams:
        if team_name:
            team, created = GameTeam.objects.get_or_create(team_name=team_name)
            if created:
                created_count += 1

    messages.success(request, f"{created_count}개의 새로운 팀을 동기화했습니다.")

@admin.register(GameTeam)
class GameTeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'unique_code', 'score')
    readonly_fields = ('unique_code',)
    actions = [sync_teams_from_profiles]
    ordering = ['team_name']

@admin.register(GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'qr_code_id', 'view_qr_code')
    readonly_fields = ('qr_code_id',)

    def view_qr_code(self, obj):
        # 각 방의 QR 코드를 관리자 페이지에서 바로 확인할 수 있는 링크를 생성합니다.
        url = reverse('recreation:play_game', args=[obj.qr_code_id])
        return format_html(f'<a href="{url}" target="_blank">QR 코드 보기/테스트</a>')
    view_qr_code.short_description = "게임 QR 코드"

@admin.register(GameProblem)
class GameProblemAdmin(admin.ModelAdmin):
    list_display = ('round_number', 'question', 'answer', 'points')
    list_editable = ('question', 'answer', 'points')

@admin.register(GameTimeSlot)
class GameTimeSlotAdmin(admin.ModelAdmin):
    list_display = ('round_number', 'start_time', 'end_time')

@admin.action(description='팀별 스케줄 자동 생성하기')
@transaction.atomic
def auto_generate_schedule(modeladmin, request, queryset):
    teams = list(GameTeam.objects.all())
    rooms = list(GameRoom.objects.exclude(name__icontains='강당'))
    timeslots = list(GameTimeSlot.objects.filter(round_number__in=[2, 3, 4, 5, 6]))

    if len(teams) != 16 or len(rooms) != 15:
        messages.error(request, "오류: 16개 팀과 15개 방('강당' 제외)이 정확히 등록되어야 합니다.")
        return

    TeamSchedule.objects.all().delete()

    try:
        auditorium = GameRoom.objects.get(name__icontains='강당')
        round1_slot = GameTimeSlot.objects.get(round_number=1)
        round7_slot = GameTimeSlot.objects.get(round_number=7)
        for team in teams:
            TeamSchedule.objects.create(team=team, timeslot=round1_slot, room=auditorium)
            TeamSchedule.objects.create(team=team, timeslot=round7_slot, room=auditorium)
    except (GameRoom.DoesNotExist, GameTimeSlot.DoesNotExist):
        messages.error(request, "오류: '강당'이라는 이름의 방과 1, 7라운드 시간이 등록되어 있어야 합니다.")
        return

    num_teams = len(teams)
    num_rooms = len(rooms)

    for timeslot in timeslots:
        room_assignments = list(range(num_rooms))
        random.shuffle(room_assignments)

        for i in range(num_teams):
            if i == 15:
                assigned_rooms_this_round = [room_assignments[j % num_rooms] for j in range(15)]
                resting_room_index = list(set(range(num_rooms)) - set(assigned_rooms_this_round))[0]
                room_index = resting_room_index
            else:
                room_index = room_assignments[i % num_rooms]

            team = teams[i]
            room = rooms[room_index]
            TeamSchedule.objects.create(team=team, timeslot=timeslot, room=room)

    messages.success(request, "모든 팀의 2~6라운드 스케줄을 성공적으로 자동 생성했습니다.")

@admin.register(TeamSchedule)
class TeamScheduleAdmin(admin.ModelAdmin):
    list_display = ('timeslot', 'team', 'room')
    list_filter = ('timeslot', 'team', 'room')
    actions = [auto_generate_schedule]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        schedule_data = {}
        teams = GameTeam.objects.order_by('team_name')
        timeslots = GameTimeSlot.objects.order_by('round_number')

        for team in teams:
            schedule_data[team.team_name] = {}
            for timeslot in timeslots:
                schedule = TeamSchedule.objects.filter(team=team, timeslot=timeslot).first()
                schedule_data[team.team_name][timeslot.round_number] = schedule.room.name if schedule else '-'

        extra_context['schedule_data'] = schedule_data
        extra_context['teams'] = teams
        extra_context['timeslots'] = timeslots

        return super().changelist_view(request, extra_context=extra_context)
