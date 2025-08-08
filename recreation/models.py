from django.db import models
import uuid
import random

class GameTeam(models.Model):
    team_name = models.CharField("팀 이름", max_length=100, unique=True)
    unique_code = models.CharField("팀 고유번호 (4자리)", max_length=4, unique=True, blank=True)
    score = models.PositiveIntegerField("총 점수", default=0)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            # 고유번호가 비어있으면, 겹치지 않는 4자리 숫자를 자동으로 생성합니다.
            while True:
                code = str(random.randint(1000, 9999))
                if not GameTeam.objects.filter(unique_code=code).exists():
                    self.unique_code = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.team_name} ({self.unique_code})"

    class Meta:
        verbose_name = "게임 팀"
        verbose_name_plural = "게임 팀 목록"

class GameRoom(models.Model):
    name = models.CharField("장소 이름", max_length=100)
    qr_code_id = models.UUIDField("QR코드 고유ID", default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "게임 장소"
        verbose_name_plural = "게임 장소 목록"

class GameProblem(models.Model):
    round_number = models.PositiveIntegerField("라운드 번호", unique=True, help_text="1~7 사이의 숫자를 입력하세요.")
    story = models.TextField("스토리", blank=True)
    question = models.TextField("문제")
    answer = models.CharField("정답", max_length=255)
    points = models.PositiveIntegerField("획득 점수", default=10)

    # --- [수정] 필드 설명을 더 명확하게 변경 ---
    completion_message = models.TextField(
        "정답/시간초과 시 메시지", 
        blank=True, 
        help_text="해당 라운드를 마쳤을 때(정답, 시간초과 포함) 보여줄 메시지입니다."
    )

    def __str__(self):
        return f"{self.round_number}라운드 문제"

    class Meta:
        verbose_name = "게임 문제"
        verbose_name_plural = "게임 문제 목록"
        ordering = ['round_number']

class GameTimeSlot(models.Model):
    round_number = models.PositiveIntegerField("라운드 번호", unique=True)
    start_time = models.DateTimeField("시작 시간 (KST)")
    end_time = models.DateTimeField("종료 시간 (KST)")

    def __str__(self):
        return f"{self.round_number}라운드 시간 ({self.start_time.strftime('%H:%M')}~{self.end_time.strftime('%H:%M')})"

    class Meta:
        verbose_name = "게임 시간"
        verbose_name_plural = "게임 시간 목록"
        ordering = ['round_number']

class TeamSchedule(models.Model):
    team = models.ForeignKey(GameTeam, on_delete=models.CASCADE, verbose_name="팀")
    timeslot = models.ForeignKey(GameTimeSlot, on_delete=models.CASCADE, verbose_name="시간")
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE, verbose_name="장소")

    def __str__(self):
        return f"[{self.timeslot.round_number}R] {self.team.team_name} -> {self.room.name}"

    class Meta:
        verbose_name = "팀별 스케줄"
        verbose_name_plural = "팀별 스케줄 표"
        # 특정 시간에 한 팀은 하나의 장소에만 있을 수 있도록 설정
        unique_together = ('team', 'timeslot')