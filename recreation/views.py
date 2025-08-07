from django.http import HttpResponse
from django.urls import reverse
import qrcode
from io import BytesIO
from .models import GameRoom

def play_game_view(request, qr_code_id):
    # 지금은 임시로 텍스트만 보여줍니다.
    return HttpResponse(f"게임방 QR ID: {qr_code_id} 에 성공적으로 접속했습니다.")

# --- [새로운 기능] QR 코드 이미지만 생성하여 보여주는 뷰 함수 ---
def generate_room_qr(request, qr_code_id):
    # 이 QR 코드가 최종적으로 연결될 게임 페이지의 전체 URL을 생성합니다.
    play_game_url = request.build_absolute_uri(
        reverse('recreation:play_game', args=[qr_code_id])
    )

    # qrcode 라이브러리를 사용하여 QR 코드 이미지를 생성합니다.
    img = qrcode.make(play_game_url)

    # 생성된 이미지를 메모리 버퍼에 PNG 형식으로 저장합니다.
    buffer = BytesIO()
    img.save(buffer, format='PNG')

    # 이미지 파일로 HTTP 응답을 반환합니다.
    return HttpResponse(buffer.getvalue(), content_type="image/png")
