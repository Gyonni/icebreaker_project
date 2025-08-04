from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import PrayerRequest
import random

def prayer_board_view(request):
    prayer_requests = PrayerRequest.objects.all()

    memo_styles = []
    colors = ['bg-yellow-200', 'bg-pink-200', 'bg-blue-200', 'bg-green-200']
    rotations = ['-rotate-3', 'rotate-2', '-rotate-1', 'rotate-1', '-rotate-2']

    for prayer in prayer_requests:
        memo_styles.append({
            'prayer': prayer,
            'color': random.choice(colors),
            'rotation': random.choice(rotations),
        })

    context = {
        'memo_styles': memo_styles
    }
    return render(request, 'prayerboard/prayer_board.html', context)

@require_POST
def add_prayer_request(request):
    content = request.POST.get('content')
    if content:
        PrayerRequest.objects.create(content=content)
        return JsonResponse({'status': 'success', 'message': '기도제목이 등록되었습니다.'})
    return JsonResponse({'status': 'error', 'message': '내용을 입력해주세요.'}, status=400)

def get_prayer_requests_api(request):
    requests = PrayerRequest.objects.values('id', 'content').order_by('-created_at')
    return JsonResponse(list(requests), safe=False)