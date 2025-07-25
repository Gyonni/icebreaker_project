from django.db import models
from django.urls import reverse
import uuid

class Person(models.Model):
    # 사용자 제공 코드 기반: UUID를 기본 키로 사용
    id = models.UUIDField("고유 ID", primary_key=True, default=uuid.uuid4, editable=False)
    
    # 엑셀 업로드 및 식별용 고유 코드
    # null=True를 추가하여 기존 데이터에 대한 마이그레이션 오류를 해결합니다.
    unique_code = models.CharField("고유번호", max_length=50, unique=True, null=True, help_text="엑셀 업로드 시 사용자를 구분하는 고유한 번호 또는 코드입니다.")

    # 기본 정보
    name = models.CharField("이름", max_length=100)
    bio = models.TextField("소개", blank=True)
    profile_image = models.ImageField("프로필 사진", upload_to='profile_images/', null=True, blank=True)

    # 연합 수련회용 정보
    GROUP_CHOICES = [
        ('주사랑교회', '주사랑교회'),
        ('예수비전교회', '예수비전교회'),
    ]
    group = models.CharField("소속", max_length=20, choices=GROUP_CHOICES, default='주사랑교회')
    team = models.CharField("팀", max_length=50, blank=True)
    
    # 인증 및 QR 관련
    auth_token = models.UUIDField("인증 토큰", default=uuid.uuid4, editable=False, unique=True, null=True, blank=True)
    is_authenticated = models.BooleanField("인증여부", default=False)
    
    # 아이스브레이킹 정보
    scanned_people = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='scanned_by', verbose_name="만난 사람")

    def __str__(self):
        return f"{self.name} ({self.unique_code or '고유번호 없음'})"

    def get_absolute_url(self):
        # 'profile_detail' URL이 profiles/urls.py에 정의되어 있어야 합니다.
        return reverse('profiles:profile_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "참가자"
        verbose_name_plural = "참가자 목록"
