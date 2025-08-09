from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from .models import GameRoom, GameTeam, TeamSchedule, GameProblem
import qrcode
from io import BytesIO

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from .models import GameRoom, GameTeam, TeamSchedule, GameProblem
import qrcode
from io import BytesIO

def play_game_view(request, qr_code_id):
    room = get_object_or_404(GameRoom, qr_code_id=qr_code_id)
    if request.method == 'POST':
        team_code = request.POST.get('unique_code')
        try:
            team = GameTeam.objects.get(unique_code=team_code)
            if team.start_time is None and team.current_round == 1:
                team.start_time = timezone.now()
                team.save()

            schedule = TeamSchedule.objects.get(team=team, round_number=team.current_round)
            if schedule.room == room:
                return render(request, 'recreation/play_arrival.html', {'team': team, 'room': room})
            else:
                messages.error(request, f"잘못된 장소입니다! '{schedule.room.name}'(으)로 이동해주세요.")
        except GameTeam.DoesNotExist:
            messages.error(request, "유효하지 않은 팀 고유번호입니다.")
        except TeamSchedule.DoesNotExist:
            messages.error(request, "게임 설정에 문제가 있습니다. 운영진에게 문의해주세요.")
        return redirect('recreation:play_game', qr_code_id=qr_code_id)
    return render(request, 'recreation/play_auth.html', {'room': room})

def submit_answer_view(request):
    if request.method == 'POST':
        team_id = request.POST.get('team_id')
        problem_id = request.POST.get('problem_id')
        submitted_answer = request.POST.get('answer', '').strip().lower()
        team = get_object_or_404(GameTeam, id=team_id)
        problem = get_object_or_404(GameProblem, id=problem_id)

        possible_answers = [ans.strip().lower() for ans in problem.answer.split('|')]
        is_correct = submitted_answer in possible_answers

        next_location_hint = ""
        is_final_round = team.current_round == 8

        if is_correct:
            if not is_final_round:
                team.current_round += 1
                next_schedule = TeamSchedule.objects.get(team=team, round_number=team.current_round)
                next_location_hint = next_schedule.room.location_hint
            else:
                if team.end_time is None: team.end_time = timezone.now()
            team.save()

        context = {
            'is_correct': is_correct, 'team': team, 'problem': problem,
            'is_final_round': is_final_round, 'next_location_hint': next_location_hint
        }
        return render(request, 'recreation/play_result.html', context)
    return redirect('core:index')

def get_problem_view(request):
    team_id = request.GET.get('team_id')
    team = get_object_or_404(GameTeam, id=team_id)
    problem = get_object_or_404(GameProblem, round_number=team.current_round)
    return render(request, 'recreation/play_problem.html', {'team': team, 'problem': problem})

def generate_room_qr(request, qr_code_id):
    play_game_url = request.build_absolute_uri(
        reverse('recreation:play_game', args=[qr_code_id])
    )
    img = qrcode.make(play_game_url)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type="image/png")

def scoreboard_view(request):
    return render(request, 'recreation/scoreboard.html')

def get_scores_api(request):
    teams = GameTeam.objects.order_by('-score', 'team_name').values('team_name', 'score')
    return JsonResponse(list(teams), safe=False)