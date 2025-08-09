from django.db import models
import uuid
import random

class GameTeam(models.Model):
    team_name = models.CharField("팀 이름", max_length=100, unique=True)
    # [수정] unique_code를 수정 가능하도록 변경 (blank=False)
    unique_code = models.CharField("팀 고유번호 (4자리)", max_length=4, unique=True)
    # [수정] score 필드 삭제, 시간 기록 및 진행 라운드 필드 추가
    start_time = models.DateTimeField("시작 시간", null=True, blank=True)
    end_time = models.DateTimeField("종료 시간", null=True, blank=True)
    current_round = models.PositiveIntegerField("현재 라운드", default=1)

    def __str__(self):
        return f"{self.team_name} ({self.unique_code})"

    class Meta:
        verbose_name = "게임 팀"
        verbose_name_plural = "게임 팀 목록"

class GameRoom(models.Model):
    name = models.CharField("장소 이름", max_length=100)
    qr_code_id = models.UUIDField("QR코드 고유ID", default=uuid.uuid4, editable=False, unique=True)
    # [새로운 기능] 장소 힌트와 정답 필드 추가
    location_hint = models.TextField("장소 힌트", blank=True)
    location_answer = models.CharField("장소 정답 (팀이 다음 장소를 찾을 때 입력)", max_length=100, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "게임 장소"
        verbose_name_plural = "게임 장소 목록"

class GameProblem(models.Model):
    round_number = models.PositiveIntegerField("라운드 번호", unique=True)
    # [수정] 일반 텍스트 필드를 텍스트 에디터 필드로 변경
    question = RichTextUploadingField("문제")
    answer = models.CharField("정답", max_length=255)
    completion_message = RichTextUploadingField("정답 시 메시지")

    def __str__(self):
        return f"{self.round_number}라운드 문제"

    class Meta:
        verbose_name = "게임 문제"
        verbose_name_plural = "게임 문제 목록"
        ordering = ['round_number']


class TeamSchedule(models.Model):
    team = models.ForeignKey(GameTeam, on_delete=models.CASCADE, verbose_name="팀")
    # [수정] timeslot 대신 round_number를 직접 사용
    round_number = models.PositiveIntegerField("라운드 번호")
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE, verbose_name="장소")

    def __str__(self):
        return f"[{self.round_number}R] {self.team.team_name} -> {self.room.name}"

    class Meta:
        verbose_name = "팀별 스케줄"
        verbose_name_plural = "팀별 스케줄 표"
        unique_together = ('team', 'round_number')