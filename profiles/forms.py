from django import forms
from .models import Person

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Person
        # 수정할 필드 목록에 'name'과 'profile_image'를 추가합니다.
        # 'fun_fact' 필드는 잠시 후 데이터베이스 모델에 추가하고 나서 다시 넣겠습니다!
        fields = ['name', 'profile_image', 'bio']
        
        # 각 필드가 HTML에서 어떻게 보일지 꾸며줍니다. (Tailwind CSS 클래스 적용)
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'w-full p-2 border rounded-md focus:ring-purple-500 focus:border-purple-500'}
            ),
            'profile_image': forms.ClearableFileInput(
                attrs={'class': 'w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100'}
            ),
            'bio': forms.Textarea(
                attrs={'rows': 5, 'class': 'w-full p-2 border rounded-md focus:ring-purple-500 focus:border-purple-500'}
            ),
        }
        
        # 각 필드의 라벨(이름표)을 한글로 예쁘게 바꿔줍니다.
        labels = {
            'name': '이름',
            'profile_image': '프로필 사진 (선택)',
            'bio': '자기소개',
        }