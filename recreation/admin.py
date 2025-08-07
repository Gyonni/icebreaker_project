from django.contrib import admin, messages
from django.db import transaction
from .models import GameTeam, GameRoom, GameProblem, GameTimeSlot, TeamSchedule
from profiles.models import Person
import random

@admin.action(description='프로필 앱의 팀 목록과 동기화하기')
def sync_teams_from_profiles(modeladmin, request, queryset):
    # profiles 앱의 Person 모델에서 고유한 팀 이름들을 가져옵니다.
    profile_teams = Person.objects.values_list('team', flat=True).distinct()

    created_count = 0
    for team_name in profile_teams:
        if team_name: # 팀 이름이 비어있지 않은 경우에만
            team, created = GameTeam.objects.get_or_create(team_name=team_name)
            if created:
                created_count += 1

    messages.success(request, f"{created_count}개의 새로운 팀을 동기화했습니다.")

@admin.register(GameTeam)
class GameTeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'unique_code', 'score')
    readonly_fields = ('unique_code',) # 자동 생성되므로 수정 불가
    actions = [sync_teams_from_profiles]

@admin.register(GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'qr_code_id')
    readonly_fields = ('qr_code_id',)

@admin.register(GameProblem)
class GameProblemAdmin(admin.ModelAdmin):
    list_display = ('round_number', 'question', 'answer', 'points')
    list_editable = ('question', 'answer', 'points')

@admin.register(GameTimeSlot)
class GameTimeSlotAdmin(admin.ModelAdmin):
    list_display = ('round_number', 'start_time', 'end_time')

@admin.action(description='팀별 스케줄 자동 생성하기')
@transaction.atomic # 작업 중 오류 발생 시, 모든 변경사항을 되돌려 데이터 무결성을 보장합니다.
def auto_generate_schedule(modeladmin, request, queryset):
    teams = list(GameTeam.objects.all())
    # 1, 7라운드는 강당이므로, 2~6라운드에 사용될 방만 가져옵니다.
    rooms = list(GameRoom.objects.exclude(name__icontains='강당'))
    timeslots = list(GameTimeSlot.objects.filter(round_number__in=[2, 3, 4, 5, 6]))

    if len(teams) != 16 or len(rooms) != 15:
        messages.error(request, "오류: 16개 팀과 15개 방('강당' 제외)이 정확히 등록되어야 합니다.")
        return

    # 기존 스케줄을 모두 삭제하고 새로 생성합니다.
    TeamSchedule.objects.all().delete()

    # 1라운드와 7라운드는 '강당'으로 고정
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

    # 2~6라운드 스케줄 자동 생성 (순환 알고리즘)
    num_teams = len(teams)
    num_rooms = len(rooms)

    for timeslot in timeslots:
        room_assignments = list(range(num_rooms))
        random.shuffle(room_assignments) # 각 라운드마다 방 순서를 섞어 예측 불가능하게 함

        for i in range(num_teams):
            # 16번째 팀은 매 라운드마다 남는 방으로 배정 (휴식 또는 특별 미션)
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
        # 관리자 페이지에 표 형식의 스케줄을 보여주기 위한 데이터 가공
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