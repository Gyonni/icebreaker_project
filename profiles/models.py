from django.db import models
from django.urls import reverse
from django.conf import settings
import uuid

class Person(models.Model):
    id = models.UUIDField("고유 ID", primary_key=True, default=uuid.uuid4, editable=False)
    unique_code = models.CharField("고유번호", max_length=50, unique=True, null=True)
    name = models.CharField("이름", max_length=100)
    bio = models.TextField("소개", blank=True)
    fun_fact = models.CharField("재미있는 사실", max_length=200, blank=True)
    profile_image = models.ImageField("프로필 사진", upload_to='profile_images/', null=True, blank=True)
    group = models.CharField("소속", max_length=20, choices=[('주사랑교회', '주사랑교회'), ('예수비전교회', '예수비전교회')], default='주사랑교회')
    team = models.CharField("팀", max_length=50, blank=True)
    auth_token = models.UUIDField("인증 토큰", default=uuid.uuid4, editable=False, unique=True, null=True, blank=True)
    is_authenticated = models.BooleanField("인증여부", default=False)
    scanned_people = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='scanned_by')
    was_picked = models.BooleanField("사회자 뽑기 여부", default=False)

    # --- [핵심 수정] 3T1L 필드 이름 및 제목 변경 ---
    sentence1 = models.CharField("문장 1", max_length=255, blank=True)
    sentence2 = models.CharField("문장 2", max_length=255, blank=True)
    sentence3 = models.CharField("문장 3", max_length=255, blank=True)
    sentence4 = models.CharField("문장 4", max_length=255, blank=True)

    LIE_CHOICES = [(1, "1번 문장"), (2, "2번 문장"), (3, "3번 문장"), (4, "4번 문장")]
    lie_answer = models.IntegerField("거짓말 정답 번호", choices=LIE_CHOICES, null=True, blank=True)

    # --- 이모티콘 카운트 필드 (이전과 동일) ---
    emoji_laughed_count = models.PositiveIntegerField("😂 받은 개수", default=0)
    emoji_touched_count = models.PositiveIntegerField("😭 받은 개수", default=0)
    emoji_tmi_count = models.PositiveIntegerField("👍 받은 개수", default=0)
    emoji_wow_count = models.PositiveIntegerField("🤯 받은 개수", default=0)

    def __str__(self):
        return f"{self.name} ({self.unique_code or '고유번호 없음'})"

    def get_absolute_url(self):
        return reverse('profiles:profile_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "참가자"
        verbose_name_plural = "참가자 목록"

class Reaction(models.Model):
    EMOJI_CHOICES = [
        ('laughed', '😂 완전 속았네!'), ('touched', '😭 감동적인 이야기'),
        ('tmi', '👍 최고의 TMI'), ('wow', '🤯 대박이에요!'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reactor = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='given_reactions')
    receiver = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='received_reactions')
    emoji_type = models.CharField("이모티콘 종류", max_length=10, choices=EMOJI_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reactor.name} -> {self.receiver.name}: {self.get_emoji_type_display()}"

    class Meta:
        verbose_name = "이모티콘 반응"
        verbose_name_plural = "이모티콘 반응 목록"
        unique_together = ('reactor', 'receiver')