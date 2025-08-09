from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
import uuid

class GameTeam(models.Model):
    team_name = models.CharField("팀 이름", max_length=100, unique=True)
    unique_code = models.CharField("팀 고유번호 (4자리)", max_length=4, unique=True)
    start_time = models.DateTimeField("시작 시간", null=True, blank=True)
    end_time = models.DateTimeField("종료 시간", null=True, blank=True)
    current_round = models.PositiveIntegerField("현재 라운드", default=1)

    def __str__(self): return f"{self.team_name} ({self.unique_code})"
    class Meta: verbose_name, verbose_name_plural = "게임 팀", "게임 팀 목록"

class GameRoom(models.Model):
    name = models.CharField("장소 이름", max_length=100)
    qr_code_id = models.UUIDField("QR코드 고유ID", default=uuid.uuid4, editable=False, unique=True)
    location_hint = models.TextField("장소 힌트", blank=True, help_text="이전 라운드를 클리어한 팀에게 보여줄 다음 장소에 대한 힌트입니다.")
    location_answer = models.CharField("장소 정답", max_length=100, blank=True, help_text="힌트를 보고 팀이 유추해야 할 이 장소의 이름입니다.")

    def __str__(self): return self.name
    class Meta: verbose_name, verbose_name_plural = "게임 장소", "게임 장소 목록"

class GameProblem(models.Model):
    round_number = models.PositiveIntegerField("라운드 번호", unique=True)
    question = RichTextUploadingField("문제 내용 (이미지, 글자 꾸밈 가능)")
    answer = models.CharField("정답", max_length=255, help_text="여러 정답이 가능할 경우, | (파이프) 기호로 구분해주세요. (예: 예수|그리스도)")
    completion_message = RichTextUploadingField("정답 시 메시지 (이미지, 글자 꾸밈 가능)")

    def __str__(self): return f"{self.round_number}라운드 문제"
    class Meta: verbose_name, verbose_name_plural = "게임 문제", "게임 문제 목록"; ordering = ['round_number']

class TeamSchedule(models.Model):
    team = models.ForeignKey(GameTeam, on_delete=models.CASCADE, verbose_name="팀")
    round_number = models.PositiveIntegerField("라운드 번호")
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE, verbose_name="장소")

    def __str__(self): return f"[{self.round_number}R] {self.team.team_name} -> {self.room.name}"
    class Meta: verbose_name, verbose_name_plural = "팀별 스케줄", "팀별 스케줄 표"; unique_together = ('team', 'round_number')