# prayerboard/models.py
from django.db import models

class PrayerRequest(models.Model):
    content = models.TextField("기도제목 내용")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"기도제목 ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        verbose_name = "익명 기도제목"
        verbose_name_plural = "익명 기도제목 목록"
        ordering = ['-created_at'] # 항상 최신순으로 정렬