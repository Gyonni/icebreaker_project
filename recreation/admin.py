from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse
from .models import GameTeam, GameRoom, GameProblem, GameTimeSlot, TeamSchedule
from profiles.models import Person
import random
import datetime

@admin.register(GameTeam)
class GameTeamAdmin(admin.ModelAdmin):
    list_display = ('team_name', 'unique_code', 'score')
    readonly_fields = ('unique_code',)
    ordering = ['team_name']

    # [핵심 수정 1] 기존 actions 설정을 삭제하고, 커스텀 템플릿을 지정합니다.
    change_list_template = "admin/recreation/gameteam/change_list.html"

    # [핵심 수정 2] 커스텀 버튼이 클릭했을 때 호출할 URL과 함수를 정의합니다.
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
    list_display = ('name', 'qr_code_id', 'view_qr_code')
    readonly_fields = ('qr_code_id',)

    def view_qr_code(self, obj):
        # 이제 'recreation:play_game' URL을 정상적으로 찾을 수 있습니다.
        url = reverse('recreation:play_game', args=[obj.qr_code_id])
        return format_html(f'<a href="{url}" target="_blank">QR 코드 보기/테스트</a>')
    view_qr_code.short_description = "게임 QR 코드"

@admin.register(GameProblem)
class GameProblemAdmin(admin.ModelAdmin):
    list_display = ('round_number', 'question', 'answer', 'points')
    list_editable = ('question', 'answer', 'points')
    ordering = ['round_number']

@admin.register(GameTimeSlot)
class GameTimeSlotAdmin(admin.ModelAdmin):
    list_display = ('round_number', 'start_time', 'end_time')
    ordering = ['round_number']
    change_list_template = "admin/recreation/gametimeslot/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        custom_urls = [
            path('auto-setup/', self.admin_site.admin_view(self.auto_setup_timeslots), name='%s_%s_auto_setup' % info),
        ]
        return custom_urls + urls

    def auto_setup_timeslots(self, request):
        start_time_str = request.POST.get('start_time')
        duration_min = int(request.POST.get('duration', 10))
        start_time = datetime.datetime.fromisoformat(start_time_str)
        GameTimeSlot.objects.all().delete()
        current_time = start_time
        for i in range(1, 8):
            end_time = current_time + datetime.timedelta(minutes=duration_min)
            GameTimeSlot.objects.create(round_number=i, start_time=current_time, end_time=end_time)
            current_time = end_time
        messages.success(request, "7개의 모든 라운드 시간이 자동으로 설정되었습니다.")
        return HttpResponseRedirect("../")

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
        # [수정] 16개의 미션방을 가져옵니다.
        rooms = list(GameRoom.objects.exclude(name__icontains='강당'))
        timeslots = list(GameTimeSlot.objects.filter(round_number__in=[2, 3, 4, 5, 6]))

        # [수정] 16개 팀과 16개 방이 있는지 확인합니다.
        if len(teams) != 16 or len(rooms) != 16:
            self.message_user(request, f"오류: 16개 팀과 16개 방('강당' 제외)이 정확히 등록되어야 합니다. (현재 팀: {len(teams)}개, 방: {len(rooms)}개)", messages.ERROR)
            return HttpResponseRedirect("../")

        TeamSchedule.objects.all().delete()

        try:
            auditorium = GameRoom.objects.get(name__icontains='강당')
            round1_slot = GameTimeSlot.objects.get(round_number=1)
            round7_slot = GameTimeSlot.objects.get(round_number=7)
            for team in teams:
                TeamSchedule.objects.create(team=team, timeslot=round1_slot, room=auditorium)
                TeamSchedule.objects.create(team=team, timeslot=round7_slot, room=auditorium)
        except (GameRoom.DoesNotExist, GameTimeSlot.DoesNotExist):
            self.message_user(request, "오류: '강당'이라는 이름의 방과 1, 7라운드 시간이 등록되어 있어야 합니다.", messages.ERROR)
            return HttpResponseRedirect("../")

        # --- [핵심 수정] 16팀-16방 스케줄 생성 알고리즘 ---
        for timeslot in timeslots:
            shuffled_teams = list(teams)
            random.shuffle(shuffled_teams)

            shuffled_rooms = list(rooms)
            random.shuffle(shuffled_rooms)

            # 16개의 팀에게 16개의 방을 하나씩 짝지어 배정합니다.
            for i in range(len(teams)):
                team = shuffled_teams[i]
                room = shuffled_rooms[i]
                TeamSchedule.objects.create(team=team, timeslot=timeslot, room=room)

        self.message_user(request, "모든 팀의 2~6라운드 스케줄을 성공적으로 자동 생성했습니다.", messages.SUCCESS)
        return HttpResponseRedirect("../")

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
