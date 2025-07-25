from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from .models import Person
from .forms import ProfileForm # 방금 만든 ProfileForm을 가져옵니다.
import qrcode
from io import BytesIO
import uuid

def profile_detail(request, pk):
    # URL로부터 대상 프로필을 가져옵니다.
    person = get_object_or_404(Person, pk=pk)
    
    # 사용자의 브라우저(세션)에 저장된 auth_token을 확인합니다.
    viewer_auth_token = request.session.get('auth_token')
    
    # auth_token을 가진 사용자가 있는지 확인합니다.
    viewer = None
    if viewer_auth_token:
        try:
            viewer = Person.objects.get(auth_token=viewer_auth_token)
        except Person.DoesNotExist:
            request.session.pop('auth_token', None)

    # "내 프로필로 만들기" 버튼을 보여줄지 결정하는 조건
    show_claim_button = (not person.is_authenticated) and (viewer is None)

    context = {
        'person': person,
        'viewer': viewer,
        'show_claim_button': show_claim_button,
    }
    return render(request, 'profiles/profile_detail.html', context)

# 프로필 수정 기능 추가
def profile_edit(request, pk):
    person = get_object_or_404(Person, pk=pk)
    
    # 본인만 수정 가능하도록 확인
    viewer_auth_token = request.session.get('auth_token')
    if str(person.auth_token) != viewer_auth_token:
        # 본인이 아니면 상세 페이지로 돌려보냄
        return redirect('profiles:profile_detail', pk=person.pk)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=person)
        if form.is_valid():
            form.save()
            return redirect('profiles:profile_detail', pk=person.pk)
    else:
        form = ProfileForm(instance=person)
        
    return render(request, 'profiles/profile_edit_form.html', {'form': form, 'person': person})

# --- 아래는 기존 인증/스캔/QR 생성 기능으로, 그대로 유지됩니다. ---

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
            return redirect(scanned_person.get_absolute_url())
        
        try:
            viewer = Person.objects.get(auth_token=viewer_auth_token)
            if viewer != scanned_person:
                viewer.scanned_people.add(scanned_person)
        except Person.DoesNotExist:
            pass
            
        return redirect(scanned_person.get_absolute_url())
    return redirect('profiles:profile_detail', pk=pk)
