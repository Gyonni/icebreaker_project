from django.http import HttpResponse

def play_game_view(request, qr_code_id):
    # 지금은 임시로 텍스트만 보여줍니다.
    return HttpResponse(f"게임방 QR ID: {qr_code_id} 에 접속했습니다.")