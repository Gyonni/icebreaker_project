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
    password = request.POST.get('password')

    if not content or not password:
        return JsonResponse({'status': 'error', 'message': '내용과 비밀번호를 모두 입력해주세요.'}, status=400)

    if not (password.isdigit() and len(password) == 4):
        return JsonResponse({'status': 'error', 'message': '비밀번호는 4자리 숫자여야 합니다.'}, status=400)

    prayer = PrayerRequest(content=content)
    prayer.set_password(password) # 비밀번호 암호화
    prayer.save()

    return JsonResponse({'status': 'success', 'message': '기도제목이 등록되었습니다.'})

# --- [새로운 기능] 기도제목을 삭제하는 뷰 ---
@require_POST
def delete_prayer_request(request, pk):
    prayer = get_object_or_404(PrayerRequest, pk=pk)
    password = request.POST.get('password')

    if not password:
        return JsonResponse({'status': 'error', 'message': '비밀번호를 입력해주세요.'}, status=400)

    if prayer.check_password(password): # 비밀번호 확인
        prayer.delete()
        return JsonResponse({'status': 'success', 'message': '기도제목이 삭제되었습니다.'})
    else:
        return JsonResponse({'status': 'error', 'message': '비밀번호가 일치하지 않습니다.'}, status=403)

def get_prayer_requests_api(request):
    requests = PrayerRequest.objects.values('id', 'content').order_by('-created_at')
    return JsonResponse(list(requests), safe=False)