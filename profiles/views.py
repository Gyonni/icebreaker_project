# 파일 경로: D:\Data\Fun\icebreaker-aws\icebreaker_project\profiles\views.py

import secrets, json
from io import BytesIO

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from urllib.parse import urljoin

import qrcode
from .models import Person
# --- [수정 1] PersonEditForm 대신 ProfileForm을 가져옵니다. ---
from .forms import ProfileForm

# 함수 이름을 profile_detail로 통일합니다. (기존 profile_view)
def profile_detail(request, pk):
    person = get_object_or_404(Person, pk=pk)
    return render(request, 'profiles/profile_detail.html', {'person': person})

# --- [수정 2] 프로필 수정 함수를 이미지 업로드에 맞게 수정합니다. ---
# URL에서 pk를 받아와 어떤 사용자를 수정할지 명확히 합니다.
def profile_edit(request, pk):
    # URL의 pk를 이용해 수정할 사람을 찾습니다.
    person = get_object_or_404(Person, pk=pk)
    
    # 사용자가 폼을 제출했을 때 (POST 요청)
    if request.method == 'POST':
        # 텍스트 데이터(request.POST)와 파일 데이터(request.FILES)를 모두 사용합니다.
        form = ProfileForm(request.POST, request.FILES, instance=person)
        if form.is_valid():
            form.save() # 변경사항 저장
            return redirect('profiles:profile_detail', pk=person.pk) # 저장 후 상세 페이지로 이동
    # 페이지에 처음 접속했을 때 (GET 요청)
    else:
        # 기존 정보가 담긴 폼을 보여줍니다.
        form = ProfileForm(instance=person)
        
    # 템플릿에 form 객체와 person 객체를 전달합니다.
    return render(request, 'profiles/profile_edit_form.html', {'form': form, 'person': person})

# --- 아래 QR코드 생성 및 인증, 스캔 관련 함수들은 님의 코드를 그대로 유지합니다. ---

def generate_qr_code(request, pk):
    person = get_object_or_404(Person, pk=pk)
    # settings.py에 SITE_URL을 추가해야 합니다. 예: SITE_URL = 'https://jusarangxjesusvision.kr'
    base_url = getattr(settings, 'SITE_URL', request.build_absolute_uri('/'))
    relative_url = person.get_absolute_url()
    profile_url = urljoin(base_url, relative_url)
    
    qr_image = qrcode.make(profile_url, box_size=10, border=4)
    
    buffer = BytesIO()
    qr_image.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type="image/png")

@csrf_exempt
@require_POST
def authenticate_device(request, pk):
    try:
        person = Person.objects.get(pk=pk)
        if person.is_authenticated:
            return JsonResponse({'status': 'error', 'message': '이미 다른 기기에서 인증이 완료된 사용자입니다.'}, status=403)
        
        new_token = secrets.token_hex(32)
        person.auth_token = new_token
        person.is_authenticated = True
        person.save()

        return JsonResponse({
            'status': 'success',
            'message': '기기 인증에 성공했습니다.',
            'user_id': person.id,
            'auth_token': new_token
        })
    except Person.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '존재하지 않는 사용자입니다.'}, status=404)

@csrf_exempt
@require_POST
def add_scanned_person(request, scanned_pk):
    try:
        data = json.loads(request.body)
        scanner_id = data.get('scanner_id')
        token = data.get('auth_token')

        if not scanner_id or not token:
            return JsonResponse({'status': 'error', 'message': '인증 정보가 누락되었습니다.'}, status=400)

        scanner = Person.objects.get(pk=scanner_id, auth_token=token)
        scanned = Person.objects.get(pk=scanned_pk)

        if scanner.pk == scanned.pk:
            return JsonResponse({'status': 'error', 'message': '자기 자신은 등록할 수 없어요!'}, status=400)
        
        if scanned in scanner.scanned_people.all():
            return JsonResponse({'status': 'success', 'message': f'{scanned.name}님은 이미 만난 사람 목록에 있습니다.'})

        scanner.scanned_people.add(scanned)
        return JsonResponse({'status': 'success', 'message': f'{scanned.name}님을 만난 사람 목록에 추가했습니다!'})

    except Person.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '인증에 실패했거나 존재하지 않는 사용자입니다.'}, status=401)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': '요청 형식이 올바르지 않습니다.'}, status=400)
