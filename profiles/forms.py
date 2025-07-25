from django import forms
from .models import Person

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Person
        # 사용자가 수정할 수 있는 필드를 지정합니다.
        fields = ['name', 'bio', 'fun_fact', 'profile_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '이름'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '간단한 자기소개'}),
            'fun_fact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'TMI, 재미있는 사실 한 가지!'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'name': '이름',
            'bio': '소개',
            'fun_fact': '재미있는 사실',
            'profile_image': '프로필 사진',
        }

