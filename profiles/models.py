from django.db import models
from django.urls import reverse
import uuid

class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="이름")
    age = models.IntegerField(null=True, blank=True, help_text="나이")
    bio = models.TextField(max_length=500, help_text="짧은 자기소개", blank=True)
    fun_fact = models.CharField(max_length=200, blank=True, help_text="재미있는 사실 한 가지")
    scanned_people = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='scanned_by')
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True, verbose_name="프로필 사진")
    
    # 서버 기반 인증을 위한 필드
    is_authenticated = models.BooleanField(default=False, help_text="이 사용자가 기기 인증을 완료했는지 여부")
    auth_token = models.CharField(max_length=64, blank=True, null=True, unique=True, help_text="인증된 기기에만 발급되는 비밀 토큰")

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('profiles:profile_detail', kwargs={'pk': self.pk})