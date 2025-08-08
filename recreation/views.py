from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import GameRoom, GameTeam, TeamSchedule, GameTimeSlot, GameProblem
import qrcode
from io import BytesIO
import random

def play_game_view(request, qr_code_id):
    room = get_object_or_404(GameRoom, qr_code_id=qr_code_id)
    if request.method == 'POST':
        team_code = request.POST.get('unique_code')
        if not team_code:
            messages.error(request, "팀 고유번호를 입력해주세요.")
            return redirect('recreation:play_game', qr_code_id=qr_code_id)
        try:
            team = GameTeam.objects.get(unique_code=team_code)
        except GameTeam.DoesNotExist:
            messages.error(request, f"'{team_code}'는 유효하지 않은 고유번호입니다.")
            return redirect('recreation:play_game', qr_code_id=qr_code_id)
        now = timezone.now()
        current_timeslot = GameTimeSlot.objects.filter(start_time__lte=now, end_time__gte=now).first()
        if not current_timeslot:
            messages.error(request, "현재 진행 중인 게임 라운드가 없습니다.")
            return redirect('recreation:play_game', qr_code_id=qr_code_id)
        schedule = TeamSchedule.objects.filter(team=team, timeslot=current_timeslot).first()
        if not schedule or schedule.room != room:
            correct_room_schedule = TeamSchedule.objects.filter(team=team, timeslot=current_timeslot).first()
            if correct_room_schedule:
                messages.error(request, f"지금은 이 방이 아닙니다! '{correct_room_schedule.room.name}'(으)로 이동해주세요.")
            else:
                messages.error(request, "스케줄 정보를 찾을 수 없습니다. 운영진에게 문의해주세요.")
            return redirect('recreation:play_game', qr_code_id=qr_code_id)
        problem = get_object_or_404(GameProblem, round_number=current_timeslot.round_number)
        context = {'team': team, 'room': room, 'problem': problem, 'timeslot': current_timeslot}
        return render(request, 'recreation/play_problem.html', context)
    context = {'room': room}
    return render(request, 'recreation/play_auth.html', context)

def submit_answer_view(request, qr_code_id):
    if request.method == 'POST':
        team_id = request.POST.get('team_id')
        problem_id = request.POST.get('problem_id')
        submitted_answer = request.POST.get('answer', '').strip()
        team = get_object_or_404(GameTeam, id=team_id)
        problem = get_object_or_404(GameProblem, id=problem_id)
        now = timezone.now()
        current_timeslot = get_object_or_404(GameTimeSlot, round_number=problem.round_number)
        result_message = ""
        is_correct = False
        if now > current_timeslot.end_time:
            result_message = "시간 초과입니다! 아쉽지만 점수를 얻지 못했습니다."
        elif problem.answer.lower() == submitted_answer.lower():
            team.score += problem.points
            team.save()
            result_message = f"정답입니다! {problem.points}점을 획득했습니다!"
            is_correct = True
        else:
            result_message = "땡! 아쉽지만 정답이 아닙니다."
        next_round_number = current_timeslot.round_number + 1
        next_location = "모든 라운드가 종료되었습니다. 강당으로 모여주세요!"
        if next_round_number <= 7:
            try:
                next_timeslot = GameTimeSlot.objects.get(round_number=next_round_number)
                next_schedule = TeamSchedule.objects.get(team=team, timeslot=next_timeslot)
                next_location = f"다음 장소는 '{next_schedule.room.name}' 입니다. 서둘러 이동해주세요!"
            except (GameTimeSlot.DoesNotExist, TeamSchedule.DoesNotExist):
                next_location = "다음 장소를 찾을 수 없습니다. 운영진에게 문의해주세요."
        context = {'result_message': result_message, 'is_correct': is_correct, 'next_location': next_location}
        return render(request, 'recreation/play_result.html', context)
    return redirect('recreation:play_game', qr_code_id=qr_code_id)

def generate_room_qr(request, qr_code_id):
    play_game_url = request.build_absolute_uri(
        reverse('recreation:play_game', args=[qr_code_id])
    )
    img = qrcode.make(play_game_url)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type="image/png")