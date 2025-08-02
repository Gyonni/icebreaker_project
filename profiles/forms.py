from django import forms
from .models import Person
from PIL import Image, ImageOps
from io import BytesIO
from django.core.files.base import ContentFile
import os

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Person
        # [수정] 필드 이름을 sentence1~4로 변경
        fields = [
            'name', 'bio', 'fun_fact', 'profile_image',
            'sentence1', 'sentence2', 'sentence3', 'sentence4', 'lie_answer'
        ]
        widgets = {
            # ... (name, bio 등은 이전과 동일) ...
            'sentence1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '첫 번째 문장'}),
            'sentence2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '두 번째 문장'}),
            'sentence3': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '세 번째 문장'}),
            'sentence4': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '네 번째 문장'}),
            'lie_answer': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': '이름', 'bio': '소개', 'fun_fact': '재미있는 사실',
            'profile_image': '프로필 사진', 'sentence1': '문장 1', 'sentence2': '문장 2',
            'sentence3': '문장 3', 'sentence4': '문장 4', 
            'lie_answer': '몇 번 문장이 거짓말인가요?',
        }

    def clean_profile_image(self, *args, **kwargs):
        image = self.cleaned_data.get("profile_image")
        if not image:
            return image
        try:
            img = Image.open(image)
            img = ImageOps.exif_transpose(img)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)
            filename_base = os.path.splitext(image.name)[0]
            new_filename = f"{filename_base}_processed.jpg"
            new_image = ContentFile(buffer.read(), name=new_filename)
            return new_image
        except Exception as e:
            raise forms.ValidationError(f"이미지 처리 중 오류가 발생했습니다: {e}")