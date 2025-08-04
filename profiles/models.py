from django.db import models
from django.urls import reverse
from django.conf import settings
import uuid

class Person(models.Model):
    id = models.UUIDField("고유 ID", primary_key=True, default=uuid.uuid4, editable=False)
    unique_code = models.CharField("고유번호", max_length=50, unique=True, null=True)
    name = models.CharField("이름", max_length=100)
    # ----------------------- 자기 소개 문답 필드와 기도제목 필드-----------------------
    bio_q1_answer = models.CharField("자기소개 답변 1", max_length=100, blank=True)
    bio_q2_answer = models.CharField("자기소개 답변 2", max_length=100, blank=True)
    bio_q3_answer = models.CharField("자기소개 답변 3", max_length=100, blank=True)
    prayer_request = models.TextField("기도제목", blank=True)
    # -----------------------------------------------------------------------------------    

    fun_fact = models.CharField("재미있는 사실", max_length=200, blank=True)
    profile_image = models.ImageField("프로필 사진", upload_to='profile_images/', null=True, blank=True)
    group = models.CharField("소속", max_length=20, choices=[('주사랑교회', '주사랑교회'), ('예수비전교회', '예수비전교회')], default='주사랑교회')
    team = models.CharField("팀", max_length=50, blank=True)
    auth_token = models.UUIDField("인증 토큰", default=uuid.uuid4, editable=False, unique=True, null=True, blank=True)
    is_authenticated = models.BooleanField("인증여부", default=False)
    scanned_people = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='scanned_by')
    # --- [새로운 기능] 사회자가 뽑았는지 여부를 기록하는 필드 ---
    was_picked = models.BooleanField("사회자 뽑기 여부", default=False)
    # --- [새로운 기능] 빙고판 순서를 저장하는 필드 ---
    # JSONField는 파이썬 리스트나 딕셔너리를 그대로 저장할 수 있어 편리합니다.
    bingo_board_layout = models.JSONField("빙고판 순서", default=list, blank=True)
    # --- [새로운 기능] TMI 추천 횟수를 기록하는 필드 ---
    tmi_recommend_count = models.PositiveIntegerField("TMI 추천수", default=0)
        
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
        
# --- [새로운 기능] 누가 누구의 TMI를 추천했는지 기록하는 모델 ---
class TmiRecommendation(models.Model):
    # 추천한 사람
    recommender = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='given_tmi_recommendations')
    # 추천받은 사람
    recommended = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='received_tmi_recommendations')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "TMI 추천 기록"
        verbose_name_plural = "TMI 추천 기록"
        # 한 사람이 다른 사람에게 추천은 한 번만 할 수 있도록 설정
        unique_together = ('recommender', 'recommended')
        
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