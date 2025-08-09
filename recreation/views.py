from django.http import HttpResponse

# urls.py에 연결된 임시 함수. GameTimeSlot을 참조하지 않습니다.
def play_game_view(request, qr_code_id):
    return HttpResponse(f"임시 게임방 QR ID: {qr_code_id}")