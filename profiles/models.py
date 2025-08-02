from django.db import models
from django.urls import reverse
import uuid

class Person(models.Model):
    id = models.UUIDField("고유 ID", primary_key=True, default=uuid.uuid4, editable=False)
    unique_code = models.CharField("고유번호", max_length=50, unique=True, null=True, help_text="엑셀 업로드 시 사용자를 구분하는 고유한 번호 또는 코드입니다.")
    name = models.CharField("이름", max_length=100)
    bio = models.TextField("소개", blank=True)
    fun_fact = models.CharField("재미있는 사실", max_length=200, blank=True)
    profile_image = models.ImageField("프로필 사진", upload_to='profile_images/', null=True, blank=True)

    GROUP_CHOICES = [ ('주사랑교회', '주사랑교회'), ('예수비전교회', '예수비전교회'), ]
    group = models.CharField("소속", max_length=20, choices=GROUP_CHOICES, default='주사랑교회')
    team = models.CharField("팀", max_length=50, blank=True)
    
    auth_token = models.UUIDField("인증 토큰", default=uuid.uuid4, editable=False, unique=True, null=True, blank=True)
    is_authenticated = models.BooleanField("인증여부", default=False)
    
    scanned_people = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='scanned_by', verbose_name="만난 사람")

    # 3T1L 필드
    truth1 = models.CharField("진실 1", max_length=255, blank=True)
    truth2 = models.CharField("진실 2", max_length=255, blank=True)
    truth3 = models.CharField("진실 3", max_length=255, blank=True)
    lie = models.CharField("거짓말", max_length=255, blank=True)
    
    LIE_CHOICES = [ (1, "1번 문장"), (2, "2번 문장"), (3, "3번 문장"), (4, "4번 문장"), ]
    lie_answer = models.IntegerField("거짓말 정답 번호", choices=LIE_CHOICES, null=True, blank=True)

    # 이모티콘 카운트 필드
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
    # ★★★ 핵심 수정: 반응을 보낸 사람(reactor)을 Person 모델과 연결 ★★★
    reactor = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='given_reactions')
    receiver = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='received_reactions')
    emoji_type = models.CharField("이모티콘 종류", max_length=10, choices=EMOJI_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reactor.name} -> {self.receiver.name}: {self.get_emoji_type_display()}"
    
    class Meta:
        verbose_name = "이모티콘 반응"
        verbose_name_plural = "이모티콘 반응 목록"
        unique_together = ('reactor', 'receiver', 'emoji_type')
