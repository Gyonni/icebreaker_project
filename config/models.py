from django.db import models

class GameStatus(models.Model):
    # 이 모델은 항상 단 하나의 설정값만 갖도록 설계됩니다.
    is_3t1l_active = models.BooleanField("3T1L 게임 활성화", default=False)
    is_bingo_active = models.BooleanField("빙고 게임 활성화", default=False)
    # --- [새로운 기능] 빙고판 섞기 가능 여부 제어 필드 ---
    can_shuffle_bingo = models.BooleanField("빙고판 섞기 활성화", default=True)
    
    def __str__(self):
        return "현재 게임 진행 상태"

    class Meta:
        verbose_name = "게임 진행 상태 관리"
        verbose_name_plural = "게임 진행 상태 관리"