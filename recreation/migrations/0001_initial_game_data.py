from django.db import migrations

def create_initial_data(apps, schema_editor):
    """
    초기 게임 데이터(방, 문제)를 생성하는 함수입니다.
    """
    GameRoom = apps.get_model('recreation', 'GameRoom')
    GameProblem = apps.get_model('recreation', 'GameProblem')

    # [수정] 17개 방 생성 (강당 1개 + 미션방 16개)
    GameRoom.objects.get_or_create(name='강당')
    for i in range(1, 17): # 15 -> 16으로 변경
        GameRoom.objects.get_or_create(name=f'미션방 {i}')

    # 7개 예시 문제 생성 (이전과 동일)
    problems_data = [
        {'round': 1, 'q': '우리의 연합 수련회 이름은?', 'a': 'JESUS VISION', 'p': 10},
        {'round': 2, 'q': '성경에서 가장 먼저 나오는 동물의 이름은?', 'a': '뱀', 'p': 20},
        {'round': 3, 'q': '예수님의 12제자가 아닌 사람은? (베드로, 요한, 바울, 안드레)', 'a': '바울', 'p': 20},
        {'round': 4, 'q': '모세가 홍해를 가를 때 사용한 지팡이의 재질은?', 'a': '나무', 'p': 20},
        {'round': 5, 'q': '다윗이 골리앗을 쓰러뜨릴 때 사용한 무기는?', 'a': '물매', 'p': 20},
        {'round': 6, 'q': '노아의 방주에 탔던 사람의 총 수는?', 'a': '8', 'p': 20},
        {'round': 7, 'q': '이번 수련회의 주제 말씀 구절은? (예: 요1:1)', 'a': '요14:6', 'p': 30},
    ]
    for data in problems_data:
        GameProblem.objects.update_or_create(
            round_number=data['round'],
            defaults={'question': data['q'], 'answer': data['a'], 'points': data['p']}
        )

class Migration(migrations.Migration):

    dependencies = [
        ('recreation', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_data),
    ]