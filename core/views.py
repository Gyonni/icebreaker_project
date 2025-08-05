from django.shortcuts import render
# profiles 앱의 Person 모델을 가져와서 사용합니다.
from profiles.models import Person

def index(request):
    # 브라우저 세션에서 사용자의 인증 토큰을 확인합니다.
    viewer_profile_id = None
    viewer_auth_token = request.session.get('auth_token')
    
    if viewer_auth_token:
        try:
            # 인증 토큰에 해당하는 사용자를 찾습니다.
            viewer = Person.objects.get(auth_token=viewer_auth_token)
            # 사용자를 찾으면, 그 사람의 고유 ID를 저장합니다.
            viewer_profile_id = viewer.id
        except Person.DoesNotExist:
            # 토큰이 유효하지 않으면 세션에서 제거합니다.
            request.session.pop('auth_token', None)
            
    context = {
        # 사용자의 프로필 ID를 템플릿으로 전달합니다. (없으면 None)
        'viewer_profile_id': viewer_profile_id
    }
    return render(request, 'core/index.html', context)

def schedule(request):
    # 수련회 일정 페이지는 변경사항이 없습니다.
    return render(request, 'core/schedule.html')


# --- [새로운 기능] 메인 홈페이지 QR 코드를 생성하는 뷰 함수 ---
def generate_homepage_qr(request):
    # 홈페이지의 전체 URL 주소를 가져옵니다. (예: https://jusarangxjesusvision.kr/)
    homepage_url = request.build_absolute_uri(reverse('core:index'))

    # qrcode 라이브러리를 사용하여 QR 코드 이미지를 생성합니다.
    img = qrcode.make(homepage_url)

    # 생성된 이미지를 메모리 버퍼에 PNG 형식으로 저장합니다.
    buffer = BytesIO()
    img.save(buffer, format='PNG')

    # 이미지 파일로 HTTP 응답을 반환합니다.
    return HttpResponse(buffer.getvalue(), content_type="image/png")