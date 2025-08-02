from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Person, Reaction
from .forms import ProfileForm
import qrcode
from io import BytesIO
import uuid
import random

def profile_detail(request, pk):
    person = get_object_or_404(Person, pk=pk)
    viewer_auth_token = request.session.get('auth_token')

    viewer = None
    if viewer_auth_token:
        try:
            viewer = Person.objects.get(auth_token=viewer_auth_token)
        except Person.DoesNotExist:
            request.session.pop('auth_token', None)

    show_claim_button = (not person.is_authenticated) and (viewer is None)
    is_already_scanned = False

    # [수정] 3T1L 문장들을 랜덤하게 섞어서 전달
    sentences = []
    lie_content = ""
    if person.lie_answer:
        all_sentences = [person.sentence1, person.sentence2, person.sentence3, person.sentence4]
        # 사용자가 선택한 정답 번호에 해당하는 문장을 lie_content로 지정
        lie_content = all_sentences[person.lie_answer - 1]

        # 화면에 보여줄 문장 목록 생성 (순서는 항상 1,2,3,4)
        sentences = [
            (1, person.sentence1), (2, person.sentence2),
            (3, person.sentence3), (4, person.sentence4)
        ]

    if viewer and person != viewer:
        is_already_scanned = viewer.scanned_people.filter(pk=person.pk).exists()

    context = {
        'person': person,
        'viewer': viewer,
        'show_claim_button': show_claim_button,
        'is_already_scanned': is_already_scanned,
        'sentences': sentences,
        'lie_answer_number': person.lie_answer,
    }
    return render(request, 'profiles/profile_detail.html', context)

# --- [새로운 기능] 3T1L 게임 플레이를 처리하는 뷰 ---
@require_POST
def play_3t1l(request, pk):
    receiver = get_object_or_404(Person, pk=pk)
    viewer_auth_token = request.session.get('auth_token')

    if not viewer_auth_token:
        return JsonResponse({'status': 'error', 'message': '인증 정보가 없습니다.'}, status=401)

    try:
        viewer = Person.objects.get(auth_token=viewer_auth_token)
    except Person.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '유효하지 않은 사용자입니다.'}, status=401)

    action = request.POST.get('action')

    if action == 'reveal_answer':
        # [수정] lie_answer를 기준으로 진짜 거짓말 문장을 찾아서 반환
        all_sentences = [receiver.sentence1, receiver.sentence2, receiver.sentence3, receiver.sentence4]
        lie_content = all_sentences[receiver.lie_answer - 1]
        return JsonResponse({'status': 'success', 'lie_answer_number': receiver.lie_answer})

    elif action == 'send_emoji':
        emoji_type = request.POST.get('emoji_type')

        # 이미 해당 이모티콘으로 반응했는지 확인
        if Reaction.objects.filter(reactor=viewer, receiver=receiver, emoji_type=emoji_type).exists():
            return JsonResponse({'status': 'info', 'message': '이미 보낸 이모티콘입니다.'})

        # 반응 기록 생성
        Reaction.objects.create(reactor=viewer, receiver=receiver, emoji_type=emoji_type)

        # 참가자의 이모티콘 카운트 증가
        if emoji_type == 'laughed':
            receiver.emoji_laughed_count += 1
        elif emoji_type == 'touched':
            receiver.emoji_touched_count += 1
        elif emoji_type == 'tmi':
            receiver.emoji_tmi_count += 1
        elif emoji_type == 'wow':
            receiver.emoji_wow_count += 1
        receiver.save()

        return JsonResponse({'status': 'success', 'message': '이모티콘을 보냈습니다!'})

    return JsonResponse({'status': 'error', 'message': '알 수 없는 요청입니다.'}, status=400)
def profile_edit(request, pk):
    person = get_object_or_404(Person, pk=pk)
    
    viewer_auth_token = request.session.get('auth_token')
    if str(person.auth_token) != viewer_auth_token:
        return redirect('profiles:profile_detail', pk=person.pk)

    if request.method == 'POST':
        # ProfileForm을 사용하므로, 폼에 정의된 이미지 리사이징 로직이 자동으로 실행됩니다.
        form = ProfileForm(request.POST, request.FILES, instance=person)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 성공적으로 수정되었습니다!')
            return redirect('profiles:profile_detail', pk=person.pk)
    else:
        form = ProfileForm(instance=person)
        
    return render(request, 'profiles/profile_edit_form.html', {'form': form, 'person': person})

def claim_profile(request, pk):
    if request.method == 'POST':
        person = get_object_or_404(Person, pk=pk)
        
        if person.is_authenticated or request.session.get('auth_token'):
            return redirect(person.get_absolute_url())

        auth_token = uuid.uuid4()
        person.auth_token = auth_token
        person.is_authenticated = True
        person.save()

        request.session['auth_token'] = str(auth_token)
        messages.success(request, f"{person.name}님의 프로필이 등록되었습니다!")
        return redirect(person.get_absolute_url())
    return redirect('profiles:profile_detail', pk=pk)

def generate_qr(request, pk):
    person = get_object_or_404(Person, pk=pk)
    qr_url = request.build_absolute_uri(reverse('profiles:profile_detail', args=[str(person.pk)]))
    
    img = qrcode.make(qr_url)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type="image/png")

def add_scanned_person(request, pk):
    if request.method == 'POST':
        scanned_person = get_object_or_404(Person, pk=pk)
        viewer_auth_token = request.session.get('auth_token')
        
        if not viewer_auth_token:
            messages.error(request, '먼저 본인의 프로필을 등록해주세요.')
            return redirect(scanned_person.get_absolute_url())
        
        try:
            viewer = Person.objects.get(auth_token=viewer_auth_token)
            if viewer != scanned_person:
                if scanned_person in viewer.scanned_people.all():
                    messages.info(request, f"{scanned_person.name}님은 이미 만난 사람 목록에 있습니다.")
                else:
                    viewer.scanned_people.add(scanned_person)
                    messages.success(request, f"{scanned_person.name}님을 만난 사람 목록에 추가했습니다!")
            else:
                messages.warning(request, '자기 자신은 추가할 수 없습니다.')
        except Person.DoesNotExist:
            messages.error(request, '인증 정보가 유효하지 않습니다. 다시 프로필을 등록해주세요.')
            
        return redirect(scanned_person.get_absolute_url())
    return redirect('profiles:profile_detail', pk=pk)
