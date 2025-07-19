import secrets, json, os
from io import BytesIO

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from urllib.parse import urljoin

import qrcode
import requests
from PIL import Image, ImageDraw, ImageFont
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
    
    # 1. QR 코드 이미지 생성
    qr_img = qrcode.make(profile_url, box_size=8, border=2).convert("RGB")

    # 2. 텍스트를 추가할 공간 확보
    qr_width, qr_height = qr_img.size
    text_area_height = 60
    total_height = qr_height + text_area_height
    
    # 3. 새로운 이미지 생성 (흰색 배경)
    final_img = Image.new('RGB', (qr_width, total_height), 'white')
    
    # 4. 새 이미지에 QR 코드 붙여넣기
    final_img.paste(qr_img, (0, 0))

    # 5. 텍스트 그리기
    draw = ImageDraw.Draw(final_img)
    
    # 폰트 파일 경로 및 URL 설정
    font_path = "/tmp/NanumGothic-Regular.ttf"
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"

    # 폰트 파일이 없으면 다운로드
    if not os.path.exists(font_path):
        try:
            response = requests.get(font_url)
            response.raise_for_status()
            with open(font_path, "wb") as f:
                f.write(response.content)
        except requests.exceptions.RequestException:
            pass # 다운로드 실패 시 그냥 넘어감
    
    try:
        font = ImageFont.truetype(font_path, 24)
    except IOError:
        font = ImageFont.load_default() # 폰트 로드 실패 시 기본 폰트 사용
    
    text = person.name
    
    # 텍스트 중앙 정렬을 위한 계산
    try:
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
    except AttributeError: # 이전 Pillow 버전 호환용
        text_width, text_height = draw.textsize(text, font=font)
    
    text_x = (qr_width - text_width) / 2
    text_y = qr_height + (text_area_height - text_height) / 2
    
    draw.text((text_x, text_y), text, font=font, fill="black")

    # 6. 최종 이미지를 버퍼에 저장하여 반환
    buffer = BytesIO()
    final_img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type="image/png")

@csrf_exempt
@require_POST
def authenticate_device(request, pk):
    # ... (이전과 동일) ...
    pass

@csrf_exempt
@require_POST
def add_scanned_person(request, scanned_pk):
    # ... (이전과 동일) ...
    pass

def edit_profile(request):
    # ... (이전과 동일) ...
    pass
