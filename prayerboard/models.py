from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class PrayerRequest(models.Model):
    content = models.TextField("기도제목 내용")
    # --- [새로운 기능] 암호화된 비밀번호를 저장할 필드 ---
    # null=True, blank=True는 기존에 비밀번호 없이 등록된 기도제목과의 호환성을 위함입니다.
    password = models.CharField("삭제용 비밀번호", max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        """비밀번호를 암호화하여 저장합니다."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """입력된 비밀번호가 저장된 비밀번호와 일치하는지 확인합니다."""
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"기도제목 ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        verbose_name = "익명 기도제목"
        verbose_name_plural = "익명 기도제목 목록"
        ordering = ['-created_at']
