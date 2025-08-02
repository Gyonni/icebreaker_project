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
from config.models import GameStatus

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

    sentences = []
    if person.sentence1 and person.sentence2 and person.sentence3 and person.sentence4 and person.lie_answer:
        sentences = [
            (1, person.sentence1), (2, person.sentence2),
            (3, person.sentence3), (4, person.sentence4)
        ]

    is_already_scanned = False
    has_reacted = False
    if viewer and person != viewer:
        is_already_scanned = viewer.scanned_people.filter(pk=person.pk).exists()
        has_reacted = Reaction.objects.filter(reactor=viewer, receiver=person).exists()

    # [핵심] 게임 활성화 상태를 데이터베이스에서 가져옵니다.
    game_status, created = GameStatus.objects.get_or_create(pk=1)

    context = {
        'person': person,
        'viewer': viewer,
        'show_claim_button': show_claim_button,
        'is_already_scanned': is_already_scanned,
        'sentences': sentences,
        'lie_answer_number': person.lie_answer,
        'has_reacted': has_reacted,
        'is_3t1l_active': game_status.is_3t1l_active,
        'is_bingo_active': game_status.is_bingo_active,
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
        all_sentences = [receiver.sentence1, receiver.sentence2, receiver.sentence3, receiver.sentence4]
        lie_content = all_sentences[receiver.lie_answer - 1]
        return JsonResponse({'status': 'success', 'lie_answer_number': receiver.lie_answer})

    elif action == 'send_emoji':
        emoji_type = request.POST.get('emoji_type')

        if Reaction.objects.filter(reactor=viewer, receiver=receiver).exists():
            return JsonResponse({'status': 'info', 'message': '이미 이모티콘을 보냈습니다.'})

        Reaction.objects.create(reactor=viewer, receiver=receiver, emoji_type=emoji_type)

        if emoji_type == 'laughed': receiver.emoji_laughed_count += 1
        elif emoji_type == 'touched': receiver.emoji_touched_count += 1
        elif emoji_type == 'tmi': receiver.emoji_tmi_count += 1
        elif emoji_type == 'wow': receiver.emoji_wow_count += 1
        receiver.save()

        # --- [핵심 수정] 이모티콘을 보내면 자동으로 만난 사람 목록에 추가합니다. ---
        if not viewer.scanned_people.filter(pk=receiver.pk).exists():
            viewer.scanned_people.add(receiver)
            message = "이모티콘을 보내고 만난 사람 목록에 추가했습니다!"
        else:
            message = "이모티콘을 보냈습니다!"

        return JsonResponse({'status': 'success', 'message': message})

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

def _create_shuffled_bingo_layout(viewer):
    """[새로운 헬퍼 함수] 섞인 빙고판 레이아웃을 생성합니다."""
    scanned_people_ids = [str(pid) for pid in viewer.scanned_people.values_list('id', flat=True)]
    board_size = 16

    # 만난 사람이 16명보다 많으면, 그 중에서 16명을 무작위로 선택합니다.
    if len(scanned_people_ids) > board_size:
        selected_ids = random.sample(scanned_people_ids, board_size)
    else:
        selected_ids = scanned_people_ids

    # 16칸을 채우기 위해 부족한 만큼 빈 칸(None)을 추가합니다.
    full_board_items = selected_ids
    while len(full_board_items) < board_size:
        full_board_items.append(None)

    # 최종 16칸(이름 + 빈 칸)을 다시 한번 섞어줍니다.
    random.shuffle(full_board_items)
    return full_board_items

def bingo_board(request):
    viewer_auth_token = request.session.get('auth_token')
    if not viewer_auth_token:
        messages.warning(request, "먼저 본인의 프로필을 등록해주세요.")
        return redirect('core:index')

    try:
        viewer = Person.objects.get(auth_token=viewer_auth_token)

        # --- [핵심 수정] 빙고판 자동 업데이트 로직 ---

        # 1. 현재 저장된 빙고판의 '사람' ID 목록을 가져옵니다.
        saved_person_ids = set([pid for pid in viewer.bingo_board_layout if pid is not None])

        # 2. 현재 '실제' 만난 사람 ID 목록을 가져옵니다.
        current_scanned_ids = set([str(pid) for pid in viewer.scanned_people.values_list('id', flat=True)])

        # 3. 두 목록이 다르거나, 빙고판이 없으면 새로 생성합니다.
        if not viewer.bingo_board_layout or saved_person_ids != current_scanned_ids:
            viewer.bingo_board_layout = _create_shuffled_bingo_layout(viewer)
            viewer.save()

        # --- (이하 로직은 이전과 동일) ---
        board_ids_with_none = viewer.bingo_board_layout
        board_ids = [pid for pid in board_ids_with_none if pid is not None]

        board_people = {str(p.id): p for p in Person.objects.filter(id__in=board_ids)}
        board_items = [board_people.get(pid) if pid is not None else None for pid in board_ids_with_none]

        game_status, _ = GameStatus.objects.get_or_create(pk=1)

        context = {
            'viewer': viewer,
            'board_items': board_items,
            'can_shuffle': game_status.can_shuffle_bingo,
        }
        return render(request, 'profiles/bingo_board.html', context)
    except Person.DoesNotExist:
        request.session.pop('auth_token', None)
        messages.error(request, "사용자 정보를 찾을 수 없습니다.")
        return redirect('core:index')

def random_profile_picker(request):
    # 사회자용 페이지를 렌더링합니다.
    return render(request, 'profiles/random_picker.html')

def get_random_profile_data(request):
    # [수정] 아직 뽑히지 않은 사람들만 대상으로 합니다.
    unpicked_people = Person.objects.filter(was_picked=False)

    if not unpicked_people:
        # 더 이상 뽑을 사람이 없을 경우
        return JsonResponse({'status': 'finished', 'message': '모든 참가자를 뽑았습니다!'})

    random_person = random.choice(unpicked_people)

    # 뽑힌 사람의 상태를 True로 변경하여 저장합니다.
    random_person.was_picked = True
    random_person.save()
    # JSON으로 전달할 데이터를 구성합니다.
    data = {
        'id': random_person.id,
        'name': random_person.name,
        'group': random_person.group,
        'team': random_person.team,
        'profile_image_url': random_person.profile_image.url if random_person.profile_image else None,
        'bio': random_person.bio,
        'fun_fact': random_person.fun_fact,
    }
    return JsonResponse(data)

# --- [새로운 기능] 모든 참가자의 뽑기 상태를 초기화하는 뷰 ---
@require_POST
def reset_all_picks(request):
    # 모든 사람의 was_picked 상태를 False로 되돌립니다.
    updated_count = Person.objects.update(was_picked=False)
    return JsonResponse({'status': 'success', 'message': f'{updated_count}명의 뽑기 상태를 초기화했습니다.'})

@require_POST
def shuffle_bingo_board(request):
    viewer_auth_token = request.session.get('auth_token')
    if viewer_auth_token:
        viewer = get_object_or_404(Person, auth_token=viewer_auth_token)
        # [수정] 헬퍼 함수를 사용하여 새로운 섞인 빙고판을 생성하고 저장합니다.
        viewer.bingo_board_layout = _create_shuffled_bingo_layout(viewer)
        viewer.save()
        messages.success(request, "빙고판을 새로 만들었습니다!")
    return redirect('profiles:bingo_board')