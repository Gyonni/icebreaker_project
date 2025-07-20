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
from .forms import PersonEditForm

def profile_view(request, pk):
    person = get_object_or_404(Person, pk=pk)
    return render(request, 'profiles/profile_detail.html', {'person': person})

def generate_qr_code(request, pk):
    person = get_object_or_404(Person, pk=pk)
    base_url = settings.SITE_URL
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

def edit_profile(request):
    if request.method == 'POST':
        token = request.POST.get('auth_token')
        user_id = request.POST.get('user_id')
        if not token or not user_id:
            return render(request, 'profiles/edit_error.html', {'message': '잘못된 접근입니다. 인증 정보가 없습니다.'})

        try:
            person = Person.objects.get(pk=user_id, auth_token=token)
            form = PersonEditForm(request.POST, instance=person)
            if form.is_valid():
                form.save()
                return redirect(person.get_absolute_url())
            else:
                return render(request, 'profiles/profile_edit_form.html', {'form': form, 'person': person})
        except Person.DoesNotExist:
            return render(request, 'profiles/edit_error.html', {'message': '인증에 실패했습니다. 다시 시도해주세요.'})
    else: # GET 요청
        # GET 요청 시에는 폼만 렌더링하고, 실제 데이터는 JS가 채웁니다.
        form = PersonEditForm()
        return render(request, 'profiles/profile_edit_form.html', {'form': form})