from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from .models import Person
# forms.py에 이미지 리사이징 기능이 추가되었습니다.
from .forms import ProfileForm 
import qrcode
from io import BytesIO
import uuid

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
    if viewer and person != viewer:
        is_already_scanned = viewer.scanned_people.filter(pk=person.pk).exists()

    context = {
        'person': person,
        'viewer': viewer,
        'show_claim_button': show_claim_button,
        'is_already_scanned': is_already_scanned,
    }
    return render(request, 'profiles/profile_detail.html', context)

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
